from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
from .models import ScheduledPost, InstagramAccount, TelegramChat
from instagrapi import Client

logger = logging.getLogger(__name__)


@shared_task
def post_to_instagram(post_id):
    """Post image to Instagram at scheduled time"""
    try:
        post = ScheduledPost.objects.get(id=post_id)
        
        if post.status == 'posted' or post.status == 'failed':
            return f"Post {post_id} already processed"
        
        # Initialize Instagram client
        client = Client()
        account = post.instagram_account
        
        # Login to Instagram
        client.login(account.username, account.password_encrypted)
        
        # Upload photo
        photo_path = post.image.path
        client.photo_upload(photo_path, caption=post.caption)
        
        # Update post status
        post.status = 'posted'
        post.posted_at = timezone.now()
        post.save()
        
        logger.info(f"Successfully posted to Instagram: {post_id}")
        
        # Notify user on Telegram
        if post.telegram_chat:
            send_telegram_notification(
                post.telegram_chat.chat_id,
                f"✅ Your post to Instagram has been posted!\n\nCaption: {post.caption[:50]}..."
            )
        
        return f"Posted successfully: {post_id}"
    
    except Exception as e:
        logger.error(f"Error posting to Instagram: {str(e)}")
        post.status = 'failed'
        post.error_message = str(e)
        post.save()
        
        if post.telegram_chat:
            send_telegram_notification(
                post.telegram_chat.chat_id,
                f"❌ Error posting to Instagram: {str(e)}"
            )
        
        return f"Failed to post: {str(e)}"


@shared_task
def check_scheduled_posts():
    """Check and execute scheduled posts that are due"""
    now = timezone.now()
    due_posts = ScheduledPost.objects.filter(
        status='scheduled',
        scheduled_time__lte=now
    )
    
    for post in due_posts:
        post_to_instagram.delay(post.id)
    
    return f"Checked {due_posts.count()} posts"


@shared_task
def send_telegram_notification(chat_id, message):
    """Send notification to Telegram"""
    from telegram import Bot
    
    try:
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message)
        return f"Message sent to {chat_id}"
    except Exception as e:
        logger.error(f"Error sending Telegram message: {str(e)}")
        return f"Failed to send message: {str(e)}"


@shared_task
def transcribe_voice_message(message_id):
    """Transcribe voice message from Telegram (placeholder)"""
    from .models import TelegramMessage
    
    try:
        msg = TelegramMessage.objects.get(id=message_id)
        
        # TODO: Implement voice-to-text transcription
        # This is a placeholder - use google-cloud-speech or similar
        
        logger.info(f"Transcribed message {message_id}")
        return f"Transcribed: {message_id}"
    
    except TelegramMessage.DoesNotExist:
        return f"Message {message_id} not found"
