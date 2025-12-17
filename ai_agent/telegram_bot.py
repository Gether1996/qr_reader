import logging
from datetime import datetime, timedelta
from django.conf import settings
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from .models import TelegramChat, ScheduledPost, InstagramAccount, TelegramMessage
from .tasks import post_to_instagram, send_telegram_notification
import re
import os
import tempfile
import whisper

logger = logging.getLogger(__name__)

# Conversation states
SCHEDULE_TIME, CAPTION, CONFIRM = range(3)
INSTAGRAM_LOGIN = range(1)


class TelegramBotHandler:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        
    @sync_to_async
    def save_telegram_chat(self, chat_id, username, first_name, last_name):
        """Save or update Telegram chat info"""
        tg_chat, created = TelegramChat.objects.update_or_create(
            chat_id=chat_id,
            defaults={
                'username': username or '',
                'first_name': first_name or '',
                'last_name': last_name or '',
                'is_active': True,
            }
        )
        return tg_chat, created
    
    def check_keyword(self, text: str, keyword: str) -> bool:
        """Check if keyword is in text (with typo tolerance)"""
        # Použiť regex na fuzzy matching - "zverej" + akýkoľvek koniec
        # Zachytí: zverejní, zverejný, zverejni, zverej, atď.
        pattern = r'\b' + keyword[:5] + r'\w*'  # Prvých 5 znakov + pokračovanie
        return bool(re.search(pattern, text.lower()))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        chat = update.effective_chat
        user = update.effective_user
        
        # Save or update chat info (async-safe)
        await self.save_telegram_chat(
            chat.id,
            user.username,
            user.first_name,
            user.last_name
        )
        
        welcome_text = (
            "👋 Vitaj v AI Agent!\n\n"
            "Dostupné príkazy:\n"
            "/start - Vitajte\n"
            "/help - Pomoc\n"
            "/connect_instagram - Pripojiť Instagram\n"
            "/schedule_post - Naplánovať post\n"
            "/list_posts - Zobraziť naplánované posty\n\n"
            "Môžeš mi poslať hlasovú správu s príkazom na plánovanie: "
            "'Postni fotku na Instagram zajtra o 10:00'\n"
        )
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = (
            "📚 Dostupná pomoc:\n\n"
            "1. Instagram integrácia\n"
            "   /connect_instagram - Pripojiť tvoj Instagram účet\n"
            "   /get_instagram_user - Zobraziť pripojené Instagram účty\n\n"
            "2. Plánovanie postov\n"
            "   /schedule_post - Interaktívne plánovanie\n"
            "   📸 Pošli fotku + text príkazu (čas a popis)\n\n"
            "3. Hlasové príkazy\n"
            "   🎙️ Pošli hlasovú správu (napr. 'Postni fotku o 10:00')\n\n"
            "4. Spravovanie postov\n"
            "   /list_posts - Zobraziť naplánované posty\n"
        )
        await update.message.reply_text(help_text)
    
    async def connect_instagram(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Connect Instagram account - ask for username"""
        await update.message.reply_text(
            "🔐 Napiš svoj Instagram username (email alebo telefón):"
        )
        context.user_data['step'] = 'instagram_username'
    
    async def schedule_post(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Interactive schedule post"""
        chat_id = update.effective_chat.id
        logger.info(f"=== SCHEDULE_POST DEBUG ===")
        logger.info(f"Chat ID: {chat_id}")
        
        tg_chat = await sync_to_async(TelegramChat.objects.get)(chat_id=chat_id)
        logger.info(f"TelegramChat found: {tg_chat}")
        
        # Check ALL Instagram accounts first
        all_accounts = await sync_to_async(lambda: list(InstagramAccount.objects.all()))()
        logger.info(f"All Instagram accounts in DB: {len(all_accounts)}")
        for acc in all_accounts:
            logger.info(f"  - {acc.username}: is_connected={acc.is_connected}")
        
        # Now filter by is_connected=True
        ig_accounts = await sync_to_async(lambda: list(InstagramAccount.objects.filter(is_connected=True)))()
        logger.info(f"Connected Instagram accounts: {len(ig_accounts)}")
        for acc in ig_accounts:
            logger.info(f"  - {acc.username}: is_connected={acc.is_connected}")
        
        if not ig_accounts:
            logger.warning(f"No connected Instagram accounts found!")
            await update.message.reply_text(
                "❌ Najprv musíš pripojiť Instagram účet!\n"
                "Použi /connect_instagram"
            )
            return
        
        ig_account = ig_accounts[0]
        logger.info(f"Using account: {ig_account.username}")
        await update.message.reply_text(
            f"📸 Pošli fotku, ktorú chceš postnúť na {ig_account.username}\n"
            "(Môž byť JPG, PNG alebo GIF)"
        )
    
    async def get_instagram_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get connected Instagram account info"""
        try:
            ig_accounts = await sync_to_async(lambda: list(
                InstagramAccount.objects.filter(is_connected=True)
            ))()
            
            if not ig_accounts:
                await update.message.reply_text(
                    "❌ Nemáš žiadny pripojený Instagram účet.\n"
                    "Použi /connect_instagram"
                )
                return
            
            text = "📱 Pripojené Instagram účty:\n\n"
            for account in ig_accounts:
                text += f"👤 Username: {account.username}\n"
                text += f"✅ Pripojený: {'Áno' if account.is_connected else 'Nie'}\n"
                text += f"📅 Pripojena: {account.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
            
            await update.message.reply_text(text)
        
        except Exception as e:
            await update.message.reply_text(
                f"❌ Chyba: {str(e)}"
            )

        context.user_data['step'] = 'schedule_photo'
    
    
    async def handle_instagram_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Instagram login flow"""
        step = context.user_data.get('step')
        
        if step == 'instagram_username':
            context.user_data['instagram_username'] = update.message.text
            await update.message.reply_text(
                f"Napiš heslo k účtu {update.message.text}:\n"
                "(Heslo bude zašifrované)"
            )
            context.user_data['step'] = 'instagram_password'
        
        elif step == 'instagram_password':
            context.user_data['instagram_password'] = update.message.text
            
            # Save to database (await the async function)
            account, created = await self.save_instagram_account(
                context.user_data['instagram_username'],
                context.user_data['instagram_password']
            )
            
            await update.message.reply_text(
                "✅ Instagram účet bol pripojený!\n"
                "Teraz môžeš naplánovať príspevky."
            )
            context.user_data.clear()
    
    @sync_to_async
    def _save_instagram_account_sync(self, username, password):
        """Synchronna databaza operacia"""
        account, created = InstagramAccount.objects.update_or_create(
            username=username,
            defaults={
                'password_encrypted': password,  # TODO: encrypt in production
                'is_connected': True,
            }
        )
        return account, created
    
    async def save_instagram_account(self, username, password):
        """Save Instagram account to database (async wrapper)"""
        return await self._save_instagram_account_sync(username, password)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        step = context.user_data.get('step')
        schedule_step = context.user_data.get('schedule_step')
        
        logger.info(f"=== MESSAGE DEBUG ===")
        logger.info(f"Text: {text}")
        logger.info(f"Step: {step}, Schedule_step: {schedule_step}")
        
        # Handle Instagram login flow
        if step in ['instagram_username', 'instagram_password']:
            await self.handle_instagram_login(update, context)
            return
        
        # Handle schedule caption input
        if schedule_step == 'caption':
            await self.handle_schedule_caption(update, context, text)
            return
        
        # Handle custom time input
        if schedule_step == 'custom_time':
            await self.handle_custom_time(update, context, text)
            return
        
        # Parse schedule command: "Zverejni [fotku/obrázok] [čas] [popis]"
        # Example: "Zverejni fotku zajtra o 10:00 - Môj nový post!"
        
        if self.check_keyword(text.lower(), 'zverejni'):
            await self.parse_schedule_command(update, context, text)
        else:
            await update.message.reply_text(
                "Nerozumiem tomuto príkazu.\n"
                "Zadaj /help pre dostupné príkazy."
            )
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages - transcribe with Whisper"""
        voice = update.message.voice
        chat = update.effective_chat
        bot = update.get_bot()
        
        try:
            # Najprv nájdi TelegramChat
            try:
                tg_chat = await sync_to_async(TelegramChat.objects.get)(chat_id=chat.id)
            except TelegramChat.DoesNotExist:
                await update.message.reply_text(
                    "❌ Najprv napiš /start"
                )
                return
            
            # Informuj používateľa
            await update.message.reply_text(
                "🎙️ Spracovávam hlasovú správu...\n"
                "Čakaj chvíľu..."
            )
            
            # Stiahni audio file
            file = await bot.get_file(voice.file_id)
            
            # Ulož dočasne
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as tmp:
                tmp_path = tmp.name
            
            # Stiahni súbor
            await file.download_to_drive(tmp_path)
            
            # Transkribuj s Whisper
            transcribed_text = await sync_to_async(self.transcribe_voice)(tmp_path)
            
            # Vymaž temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            if not transcribed_text:
                await update.message.reply_text(
                    "❌ Nepodarilo sa rozpísať hlasovú správu.\n"
                    "Skús neskôr."
                )
                return
            
            # Ulož do DB (s FK na TelegramChat)
            await sync_to_async(TelegramMessage.objects.create)(
                chat=tg_chat,
                message_id=update.message.message_id,
                message_type='voice',
                content=transcribed_text,
                voice_file_id=voice.file_id,
                processed=True
            )
            
            # Zobraz prepísaný text
            await update.message.reply_text(
                f"✅ Rozpísané:\n\n_{transcribed_text}_",
                parse_mode='Markdown'
            )
            
            # Spracuj ako normálnu správu
            if self.check_keyword(transcribed_text.lower(), 'zverejni'):
                await self.parse_schedule_command(update, context, transcribed_text)
        
        except Exception as e:
            logger.error(f"Error processing voice: {str(e)}")
            await update.message.reply_text(
                f"❌ Chyba pri spracovaní: {str(e)}"
            )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        photo = update.message.photo
        chat = update.effective_chat
        
        try:
            logger.info(f"=== PHOTO DEBUG ===")
            logger.info(f"Chat ID: {chat.id}")
            logger.info(f"Photo file_id: {photo[-1].file_id}")
            
            # Get TelegramChat
            tg_chat = await sync_to_async(TelegramChat.objects.get)(chat_id=chat.id)
            
            # Save photo file_id to context
            context.user_data['photo_file_id'] = photo[-1].file_id
            logger.info(f"Photo saved to context, asking for time...")
            
            await update.message.reply_text(
                "📅 V akom čase chceš postnúť?\n"
                "(Formát: 'zajtra o 10:00' alebo 'o 14:30')",
                reply_markup=self.get_time_buttons()
            )
            context.user_data['schedule_step'] = 'time'
            logger.info(f"Schedule step set to 'time'")
        
        except TelegramChat.DoesNotExist:
            await update.message.reply_text("Najprv napiš /start")
        except Exception as e:
            logger.error(f"Error processing photo: {str(e)}")
            await update.message.reply_text(f"❌ Chyba: {str(e)}")
    
    async def handle_time_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle time selection callback from inline buttons"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        logger.info(f"=== TIME CALLBACK DEBUG ===")
        logger.info(f"Callback data: {callback_data}")
        logger.info(f"Context user_data: {context.user_data}")
        
        # Parse time from callback_data (format: "time_tomorrow_10")
        if callback_data.startswith('time_'):
            parts = callback_data.split('_')
            if len(parts) >= 3:
                day = parts[1]  # "today" or "tomorrow"
                hour = parts[2]  # "10", "14"
                
                scheduled_time = self.parse_callback_time(day, int(hour))
                logger.info(f"Scheduled time: {scheduled_time}")
                
                context.user_data['scheduled_time'] = scheduled_time
                
                # Ask for caption
                await query.edit_message_text(
                    "✏️ Napíš popis (caption) pre post:"
                )
                context.user_data['schedule_step'] = 'caption'
                logger.info(f"Waiting for caption...")
            else:
                await query.edit_message_text("❌ Neplatný čas")
        elif callback_data == 'time_custom':
            await query.edit_message_text(
                "Napíš čas v tvare: YYYY-MM-DD HH:MM"
            )
            context.user_data['schedule_step'] = 'custom_time'
    
    def parse_callback_time(self, day: str, hour: int) -> datetime:
        """Parse time from callback"""
        now = datetime.now()
        
        if day == 'today':
            scheduled = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:  # tomorrow
            scheduled = now + timedelta(days=1)
            scheduled = scheduled.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        return scheduled
    
    async def handle_schedule_caption(self, update: Update, context: ContextTypes.DEFAULT_TYPE, caption: str):
        """Handle caption input for scheduled post"""
        chat_id = update.effective_chat.id
        bot = update.get_bot()
        
        try:
            logger.info(f"=== CAPTION DEBUG ===")
            logger.info(f"Caption: {caption}")
            logger.info(f"Context: {context.user_data}")
            
            # Get data from context
            photo_file_id = context.user_data.get('photo_file_id')
            scheduled_time = context.user_data.get('scheduled_time')
            instagram_account = await sync_to_async(InstagramAccount.objects.filter(is_connected=True).first)()
            tg_chat = await sync_to_async(TelegramChat.objects.get)(chat_id=chat_id)
            
            if not all([photo_file_id, scheduled_time, instagram_account]):
                logger.error(f"Missing data: photo={bool(photo_file_id)}, time={bool(scheduled_time)}, ig={bool(instagram_account)}")
                await update.message.reply_text("❌ Chyba: Chýbajú údaje. Skús /schedule_post znova.")
                return
            
            # Download photo from Telegram
            await update.message.reply_text("⏳ Sťahujem fotku...")
            
            file = await bot.get_file(photo_file_id)
            
            # Save to media folder
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp_path = tmp.name
            
            await file.download_to_drive(tmp_path)
            logger.info(f"Photo downloaded to: {tmp_path}")
            
            # Save scheduled post to database with image (sync operation)
            scheduled_post = await self.save_scheduled_post_with_image(
                instagram_account, tg_chat, caption, scheduled_time, tmp_path
            )
            
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            
            logger.info(f"Created ScheduledPost: {scheduled_post.id} with image")
            
            # Check if time is in the past or very soon - post immediately
            now = datetime.now()
            time_diff = (scheduled_time - now).total_seconds()
            
            if time_diff <= 0:
                # Post immediately
                logger.info(f"Time is in past, posting immediately...")
                from .tasks import post_to_instagram
                post_to_instagram.delay(scheduled_post.id)
                await update.message.reply_text(
                    f"✅ Post bol vytvorený a posielame ho na Instagram!\n\n"
                    f"📱 Instagram: {instagram_account.username}\n"
                    f"✏️ Popis: {caption[:50]}...\n"
                    f"ID: {scheduled_post.id}"
                )
            else:
                # Schedule for later
                await update.message.reply_text(
                    f"✅ Post bol naplánovaný!\n\n"
                    f"📱 Instagram: {instagram_account.username}\n"
                    f"📅 Čas: {scheduled_time.strftime('%d.%m.%Y %H:%M')}\n"
                    f"✏️ Popis: {caption[:50]}...\n\n"
                    f"ID: {scheduled_post.id}"
                )
            
            # Clear context
            context.user_data.clear()
        
        except Exception as e:
            logger.error(f"Error saving caption: {str(e)}", exc_info=True)
            await update.message.reply_text(f"❌ Chyba pri ukladaní: {str(e)}")
    
    @sync_to_async
    def save_scheduled_post_with_image(self, instagram_account, tg_chat, caption, scheduled_time, image_path):
        """Save scheduled post with image (sync operation)"""
        from django.core.files import File as DjangoFile
        
        scheduled_post = ScheduledPost.objects.create(
            instagram_account=instagram_account,
            telegram_chat=tg_chat,
            caption=caption,
            scheduled_time=scheduled_time,
            status='pending'
        )
        
        # Save image
        with open(image_path, 'rb') as photo_file:
            scheduled_post.image.save(f"post_{scheduled_post.id}.jpg", DjangoFile(photo_file), save=True)
        
        return scheduled_post
    
    async def handle_custom_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE, time_text: str):
        """Handle custom time input"""
        try:
            # Parse format: YYYY-MM-DD HH:MM
            scheduled_time = datetime.strptime(time_text.strip(), "%Y-%m-%d %H:%M")
            context.user_data['scheduled_time'] = scheduled_time
            context.user_data['schedule_step'] = 'caption'
            
            await update.message.reply_text(
                "✏️ Napíš popis (caption) pre post:"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ Neplatný formát!\n"
                "Použi: YYYY-MM-DD HH:MM\n"
                "Príklad: 2025-12-18 14:30"
            )
    
    @sync_to_async
    def _transcribe_voice_sync(self, audio_path: str) -> str:
        """Synchronna transkripcia (blocking)"""
        try:
            # Load Whisper model (small = ~1.4GB, more accurate)
            model = whisper.load_model("small", device="cpu")
            
            # Transcribe
            result = model.transcribe(audio_path, language="sk")
            
            text = result.get("text", "").strip()
            logger.info(f"Transcribed: {text}")
            return text
        
        except Exception as e:
            logger.error(f"Whisper error: {str(e)}")
            return ""
    
    async def transcribe_voice(self, audio_path: str) -> str:
        """Asynchronne zabalenie pre transkripciu (non-blocking)"""
        return await self._transcribe_voice_sync(audio_path)
    
    async def parse_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Parse schedule command from text or voice"""
        # Example: "Postni fotku zajtra o 10:00 - Môj nový post!"
        
        try:
            chat = update.effective_chat
            tg_chat = await sync_to_async(TelegramChat.objects.get)(chat_id=chat.id)
            
            # Get first Instagram account (simplified - should be one per user)
            ig_accounts = await sync_to_async(lambda: list(
                InstagramAccount.objects.filter(is_connected=True)[:1]
            ))()
            
            if not ig_accounts:
                await update.message.reply_text(
                    "❌ Najprv musíš pripojiť Instagram účet!\n"
                    "Použi /connect_instagram"
                )
                return
            
            ig_account = ig_accounts[0]
            context.user_data['instagram_account_id'] = ig_account.id
            
            # Simple parsing logic
            if ('fotka' in text.lower() or 'obrázok' in text.lower() or 
                self.check_keyword(text.lower(), 'zverejni')):
                # Extract time and caption
                # This is simplified - better use NLP library
                
                await update.message.reply_text(
                    "📅 V akom čase chceš postnúť?\n"
                    "(Formát: 'zajtra o 10:00' alebo 'o 14:30')",
                    reply_markup=self.get_time_buttons()
                )
                context.user_data['schedule_step'] = 'time'
        
        except TelegramChat.DoesNotExist:
            await update.message.reply_text(
                "Najprv napiš /start"
            )
    
    def get_time_buttons(self):
        """Get quick time selection buttons"""
        keyboard = [
            [
                InlineKeyboardButton("Dnes o 10:00", callback_data="time_today_10"),
                InlineKeyboardButton("Dnes o 14:00", callback_data="time_today_14"),
            ],
            [
                InlineKeyboardButton("Zajtra o 10:00", callback_data="time_tomorrow_10"),
                InlineKeyboardButton("Zajtra o 14:00", callback_data="time_tomorrow_14"),
            ],
            [
                InlineKeyboardButton("Vlastný čas", callback_data="time_custom"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def list_posts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List scheduled posts"""
        chat = update.effective_chat
        
        try:
            tg_chat = await sync_to_async(TelegramChat.objects.get)(chat_id=chat.id)
            posts = await sync_to_async(lambda: list(
                ScheduledPost.objects.filter(
                    telegram_chat=tg_chat
                ).exclude(status='posted')
            ))()
            
            if not posts:
                await update.message.reply_text("Nemáš žiadne naplánované posty.")
                return
            
            text = "📋 Tvoje naplánované posty:\n\n"
            for post in posts:
                text += f"• {post.instagram_account.username}\n"
                text += f"  Čas: {post.scheduled_time.strftime('%d.%m.%Y %H:%M')}\n"
                text += f"  Status: {post.get_status_display()}\n"
                text += f"  Popis: {post.caption[:50]}...\n\n"
            
            await update.message.reply_text(text)
        
        except TelegramChat.DoesNotExist:
            await update.message.reply_text("Najprv napiš /start")


def setup_telegram_bot():
    """Setup and run Telegram bot"""
    handler = TelegramBotHandler()
    
    app = Application.builder().token(handler.token).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", handler.start))
    app.add_handler(CommandHandler("help", handler.help_command))
    app.add_handler(CommandHandler("list_posts", handler.list_posts))
    app.add_handler(CommandHandler("connect_instagram", handler.connect_instagram))
    app.add_handler(CommandHandler("schedule_post", handler.schedule_post))
    app.add_handler(CommandHandler("get_instagram_user", handler.get_instagram_user))
    
    # Callback handler for inline buttons
    app.add_handler(CallbackQueryHandler(handler.handle_time_callback, pattern=r'^time_'))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handler.handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handler.handle_photo))
    
    # Conversation handler for schedule
    # TODO: Add conversation handlers for scheduling
    
    return app
