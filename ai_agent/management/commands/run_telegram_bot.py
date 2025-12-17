import asyncio
import logging
from django.core.management.base import BaseCommand
from ai_agent.telegram_bot import setup_telegram_bot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Start Telegram bot for AI Agent'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram bot...'))
        
        app = setup_telegram_bot()
        
        # Run bot with polling
        app.run_polling()
