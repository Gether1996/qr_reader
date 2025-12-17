from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TelegramChat(models.Model):
    """Telegram chat a user information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_chat', null=True, blank=True)
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} (@{self.username})"

    class Meta:
        verbose_name = "Telegram Chat"
        verbose_name_plural = "Telegram Chats"


class InstagramAccount(models.Model):
    """Instagram account information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instagram_account', null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    password_encrypted = models.CharField(max_length=500)  # Encrypted password
    is_connected = models.BooleanField(default=False)
    session_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} (Instagram)"

    class Meta:
        verbose_name = "Instagram Account"
        verbose_name_plural = "Instagram Accounts"


class ScheduledPost(models.Model):
    """Scheduled Instagram posts"""
    POST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('posted', 'Posted'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    instagram_account = models.ForeignKey(InstagramAccount, on_delete=models.CASCADE, related_name='scheduled_posts')
    telegram_chat = models.ForeignKey(TelegramChat, on_delete=models.SET_NULL, null=True, related_name='scheduled_posts')
    caption = models.TextField()
    image = models.ImageField(upload_to='instagram_posts/')
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=POST_STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.instagram_account.username} at {self.scheduled_time}"

    class Meta:
        verbose_name = "Scheduled Post"
        verbose_name_plural = "Scheduled Posts"
        ordering = ['-scheduled_time']


class TelegramMessage(models.Model):
    """Log of Telegram messages"""
    chat = models.ForeignKey(TelegramChat, on_delete=models.CASCADE, related_name='messages')
    message_id = models.BigIntegerField()
    message_type = models.CharField(max_length=50, choices=[
        ('text', 'Text'),
        ('voice', 'Voice'),
        ('photo', 'Photo'),
        ('document', 'Document'),
        ('other', 'Other'),
    ])
    content = models.TextField()
    voice_file_id = models.CharField(max_length=500, blank=True)  # Telegram file_id
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.chat.username} ({self.message_type})"

    class Meta:
        verbose_name = "Telegram Message"
        verbose_name_plural = "Telegram Messages"
