from django.contrib import admin
from .models import N8nWorkflow, N8nWebhook, N8nExecutionLog, N8nTrigger


@admin.register(N8nWorkflow)
class N8nWorkflowAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow_id', 'is_active', 'created_at', 'created_by']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'workflow_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Základné informácie', {
            'fields': ('name', 'workflow_id', 'description', 'is_active')
        }),
        ('Konfigurácia', {
            'fields': ('webhook_url',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(N8nWebhook)
class N8nWebhookAdmin(admin.ModelAdmin):
    list_display = ['name', 'endpoint', 'webhook_type', 'workflow', 'is_active', 'created_at']
    list_filter = ['webhook_type', 'is_active', 'created_at']
    search_fields = ['name', 'endpoint']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Základné informácie', {
            'fields': ('name', 'endpoint', 'webhook_type', 'workflow', 'is_active')
        }),
        ('Bezpečnosť', {
            'fields': ('secret_key',)
        }),
        ('Konfigurácia', {
            'fields': ('headers', 'config'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(N8nExecutionLog)
class N8nExecutionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'workflow', 'status', 'user', 'started_at', 'duration_ms']
    list_filter = ['status', 'started_at', 'workflow']
    search_fields = ['execution_id', 'error_message']
    readonly_fields = ['created_at', 'started_at', 'finished_at', 'duration_ms']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Základné informácie', {
            'fields': ('workflow', 'webhook', 'execution_id', 'status')
        }),
        ('Data', {
            'fields': ('request_data', 'response_data', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('user', 'ip_address', 'user_agent'),
        }),
        ('Časové údaje', {
            'fields': ('started_at', 'finished_at', 'duration_ms', 'created_at'),
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(N8nTrigger)
class N8nTriggerAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'workflow', 'is_active', 'trigger_count', 'last_triggered_at']
    list_filter = ['trigger_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['trigger_count', 'last_triggered_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Základné informácie', {
            'fields': ('name', 'trigger_type', 'workflow', 'is_active')
        }),
        ('Podmienky', {
            'fields': ('conditions',),
            'classes': ('collapse',)
        }),
        ('Štatistiky', {
            'fields': ('trigger_count', 'last_triggered_at'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
