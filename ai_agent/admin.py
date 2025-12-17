from django.contrib import admin
from .models import TelegramChat, InstagramAccount, ScheduledPost, TelegramMessage


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('username', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(InstagramAccount)
class InstagramAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'is_connected', 'created_at')
    list_filter = ('is_connected', 'created_at')
    search_fields = ('username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = ('instagram_account', 'status', 'scheduled_time', 'created_at')
    list_filter = ('status', 'scheduled_time', 'created_at')
    search_fields = ('instagram_account__username', 'caption')
    readonly_fields = ('created_at', 'updated_at', 'posted_at')
    fieldsets = (
        ('Instagram Info', {
            'fields': ('instagram_account', 'telegram_chat')
        }),
        ('Post Details', {
            'fields': ('image', 'caption', 'scheduled_time')
        }),
        ('Status', {
            'fields': ('status', 'error_message', 'posted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'message_type', 'processed', 'created_at')
    list_filter = ('message_type', 'processed', 'created_at')
    search_fields = ('chat__username', 'content')
    readonly_fields = ('created_at',)
