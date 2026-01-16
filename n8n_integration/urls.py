from django.urls import path
from . import views

app_name = 'n8n_integration'

urlpatterns = [
    # Webhook receiver
    path('webhook/<str:endpoint>/', views.webhook_receiver, name='webhook_receiver'),
    
    # Trigger workflow
    path('trigger/<str:workflow_id>/', views.trigger_workflow, name='trigger_workflow'),
    
    # UI Views
    path('workflows/', views.workflow_list, name='workflow_list'),
    path('workflows/<str:workflow_id>/', views.workflow_detail, name='workflow_detail'),
    path('executions/', views.execution_logs, name='execution_logs'),
    
    # API Endpoints
    path('api/workflows/', views.api_workflows, name='api_workflows'),
    path('api/stats/<str:workflow_id>/', views.api_execution_stats, name='api_execution_stats'),
]
