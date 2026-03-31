from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
import json


class N8nWorkflow(models.Model):
    """Model pre ukladanie informácií o n8n workflow"""
    
    name = models.CharField(max_length=255, verbose_name="Názov workflow")
    workflow_id = models.CharField(max_length=100, unique=True, verbose_name="n8n Workflow ID")
    description = models.TextField(blank=True, verbose_name="Popis")
    is_active = models.BooleanField(default=True, verbose_name="Aktívny")
    webhook_url = models.URLField(max_length=500, blank=True, verbose_name="Webhook URL")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvorené")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualizované")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_workflows')
    
    class Meta:
        verbose_name = "n8n Workflow"
        verbose_name_plural = "n8n Workflows"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.workflow_id})"


class N8nWebhook(models.Model):
    """Model pre ukladanie webhook endpointov pre n8n"""
    
    WEBHOOK_TYPES = [
        ('incoming', 'Prichádzajúci (od n8n)'),
        ('outgoing', 'Odchádzajúci (do n8n)'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Názov webhooku")
    endpoint = models.CharField(max_length=255, unique=True, verbose_name="Endpoint URL")
    webhook_type = models.CharField(max_length=20, choices=WEBHOOK_TYPES, default='incoming', verbose_name="Typ webhooku")
    workflow = models.ForeignKey(N8nWorkflow, on_delete=models.CASCADE, related_name='webhooks', null=True, blank=True)
    
    secret_key = models.CharField(max_length=255, blank=True, verbose_name="Tajný kľúč")
    is_active = models.BooleanField(default=True, verbose_name="Aktívny")
    
    # Metadata
    headers = models.JSONField(default=dict, blank=True, verbose_name="HTTP Headers")
    config = models.JSONField(default=dict, blank=True, verbose_name="Konfigurácia")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvorené")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualizované")
    
    class Meta:
        verbose_name = "n8n Webhook"
        verbose_name_plural = "n8n Webhooky"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.endpoint}"


class N8nExecutionLog(models.Model):
    """Model pre logovanie vykonaní workflow"""
    
    STATUS_CHOICES = [
        ('pending', 'Čakajúce'),
        ('running', 'Bežiace'),
        ('success', 'Úspešné'),
        ('error', 'Chyba'),
        ('cancelled', 'Zrušené'),
    ]
    
    workflow = models.ForeignKey(N8nWorkflow, on_delete=models.CASCADE, related_name='executions', null=True, blank=True)
    webhook = models.ForeignKey(N8nWebhook, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    
    execution_id = models.CharField(max_length=100, blank=True, verbose_name="Execution ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Stav")
    
    # Data
    request_data = models.JSONField(default=dict, verbose_name="Request Data")
    response_data = models.JSONField(default=dict, blank=True, verbose_name="Response Data")
    error_message = models.TextField(blank=True, verbose_name="Chybová správa")
    
    # Metadata
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Používateľ")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresa")
    user_agent = models.CharField(max_length=500, blank=True, verbose_name="User Agent")
    
    # Timestamps
    started_at = models.DateTimeField(default=datetime.now, verbose_name="Začaté")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Skončené")
    duration_ms = models.IntegerField(null=True, blank=True, verbose_name="Trvanie (ms)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvorené")
    
    class Meta:
        verbose_name = "n8n Execution Log"
        verbose_name_plural = "n8n Execution Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['workflow']),
        ]
    
    def __str__(self):
        workflow_name = self.workflow.name if self.workflow else "N/A"
        return f"{workflow_name} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def mark_success(self, response_data=None):
        """Označí execution ako úspešný"""
        self.status = 'success'
        self.finished_at = datetime.now()
        if self.started_at:
            delta = self.finished_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)
        if response_data:
            self.response_data = response_data
        self.save()
    
    def mark_error(self, error_message):
        """Označí execution ako chybný"""
        self.status = 'error'
        self.finished_at = datetime.now()
        if self.started_at:
            delta = self.finished_at - self.started_at
            self.duration_ms = int(delta.total_seconds() * 1000)
        self.error_message = error_message
        self.save()


class N8nTrigger(models.Model):
    """Model pre automatické triggere pre n8n workflows"""
    
    TRIGGER_TYPES = [
        ('scan', 'QR Scan'),
        ('user_register', 'Registrácia používateľa'),
        ('vacation_request', 'Žiadosť o dovolenku'),
        ('magazine_publish', 'Publikácia magazínu'),
        ('custom', 'Vlastný'),
    ]
    
    name = models.CharField(max_length=255, verbose_name="Názov triggeru")
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES, verbose_name="Typ triggeru")
    workflow = models.ForeignKey(N8nWorkflow, on_delete=models.CASCADE, related_name='triggers')
    
    is_active = models.BooleanField(default=True, verbose_name="Aktívny")
    
    # Podmienky
    conditions = models.JSONField(default=dict, blank=True, verbose_name="Podmienky spustenia")
    
    # Štatistiky
    trigger_count = models.IntegerField(default=0, verbose_name="Počet spustení")
    last_triggered_at = models.DateTimeField(null=True, blank=True, verbose_name="Posledné spustenie")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Vytvorené")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Aktualizované")
    
    class Meta:
        verbose_name = "n8n Trigger"
        verbose_name_plural = "n8n Triggery"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"
    
    def increment_count(self):
        """Zvýši počítadlo spustení"""
        self.trigger_count += 1
        self.last_triggered_at = datetime.now()
        self.save(update_fields=['trigger_count', 'last_triggered_at'])
