from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.db import models
import json
import requests
import hashlib
import hmac

from .models import N8nWorkflow, N8nWebhook, N8nExecutionLog, N8nTrigger


def get_client_ip(request):
    """Získaj IP adresu klienta"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verify_webhook_signature(request, secret_key):
    """Overí webhook signature"""
    if not secret_key:
        return True
    
    signature = request.headers.get('X-N8N-Signature', '')
    if not signature:
        return False
    
    body = request.body
    expected_signature = hmac.new(
        secret_key.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


@csrf_exempt
@require_http_methods(["POST", "GET"])
def webhook_receiver(request, endpoint):
    """
    Univerzálny webhook receiver pre n8n
    URL: /n8n/webhook/<endpoint>/
    """
    try:
        webhook = N8nWebhook.objects.get(endpoint=endpoint, is_active=True)
    except N8nWebhook.DoesNotExist:
        return JsonResponse({'error': 'Webhook not found'}, status=404)
    
    # Overiť signature ak existuje
    if webhook.secret_key and not verify_webhook_signature(request, webhook.secret_key):
        return JsonResponse({'error': 'Invalid signature'}, status=403)
    
    # Získať data
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {'raw': request.body.decode('utf-8')}
    else:
        data = dict(request.GET)
    
    # Zaznamenať execution
    execution_log = N8nExecutionLog.objects.create(
        webhook=webhook,
        workflow=webhook.workflow,
        request_data=data,
        status='running',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        user=request.user if request.user.is_authenticated else None
    )
    
    # Spracovať webhook
    try:
        # Tu môžeš pridať vlastnú logiku
        response_data = {
            'status': 'success',
            'message': 'Webhook received',
            'execution_id': execution_log.id,
            'timestamp': timezone.now().isoformat()
        }
        
        execution_log.mark_success(response_data)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        execution_log.mark_error(str(e))
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def trigger_workflow(request, workflow_id):
    """
    Spustí n8n workflow manuálne
    URL: /n8n/trigger/<workflow_id>/
    """
    try:
        workflow = N8nWorkflow.objects.get(workflow_id=workflow_id, is_active=True)
    except N8nWorkflow.DoesNotExist:
        return JsonResponse({'error': 'Workflow not found'}, status=404)
    
    if not workflow.webhook_url:
        return JsonResponse({'error': 'Workflow webhook URL not configured'}, status=400)
    
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Pridať metadata
    data['_metadata'] = {
        'user_id': request.user.id,
        'username': request.user.username,
        'triggered_at': timezone.now().isoformat(),
        'source': 'django_app'
    }
    
    # Zaznamenať execution
    execution_log = N8nExecutionLog.objects.create(
        workflow=workflow,
        request_data=data,
        status='running',
        user=request.user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    try:
        # Poslať request do n8n
        response = requests.post(
            workflow.webhook_url,
            json=data,
            timeout=30
        )
        
        response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'raw': response.text}
        
        if response.status_code in [200, 201]:
            execution_log.mark_success(response_data)
            return JsonResponse({
                'status': 'success',
                'execution_id': execution_log.id,
                'response': response_data
            })
        else:
            execution_log.mark_error(f"HTTP {response.status_code}: {response.text}")
            return JsonResponse({
                'error': f"Workflow returned status {response.status_code}",
                'details': response_data
            }, status=response.status_code)
            
    except requests.exceptions.RequestException as e:
        execution_log.mark_error(str(e))
        return JsonResponse({'error': f'Request failed: {str(e)}'}, status=500)


@login_required
def workflow_list(request):
    """Zobrazí zoznam všetkých workflows"""
    workflows = N8nWorkflow.objects.filter(is_active=True)
    return render(request, 'n8n_integration/workflow_list.html', {
        'workflows': workflows
    })


@login_required
def workflow_detail(request, workflow_id):
    """Detail workflow s históriou executions"""
    workflow = get_object_or_404(N8nWorkflow, workflow_id=workflow_id)
    executions = workflow.executions.all()[:50]
    
    return render(request, 'n8n_integration/workflow_detail.html', {
        'workflow': workflow,
        'executions': executions
    })


@login_required
def execution_logs(request):
    """Zobrazí všetky execution logy"""
    logs = N8nExecutionLog.objects.all()[:100]
    
    # Filtre
    status = request.GET.get('status')
    if status:
        logs = logs.filter(status=status)
    
    workflow_id = request.GET.get('workflow')
    if workflow_id:
        logs = logs.filter(workflow__workflow_id=workflow_id)
    
    return render(request, 'n8n_integration/execution_logs.html', {
        'logs': logs
    })


@login_required
@require_http_methods(["GET"])
def api_workflows(request):
    """API endpoint pre zoznam workflows"""
    workflows = N8nWorkflow.objects.filter(is_active=True)
    data = [{
        'id': w.workflow_id,
        'name': w.name,
        'description': w.description,
        'webhook_url': w.webhook_url,
        'created_at': w.created_at.isoformat(),
    } for w in workflows]
    
    return JsonResponse({'workflows': data})


@login_required
@require_http_methods(["GET"])
def api_execution_stats(request, workflow_id):
    """Štatistiky pre konkrétny workflow"""
    workflow = get_object_or_404(N8nWorkflow, workflow_id=workflow_id)
    
    executions = workflow.executions.all()
    total = executions.count()
    success = executions.filter(status='success').count()
    error = executions.filter(status='error').count()
    pending = executions.filter(status='pending').count()
    
    # Priemerný čas
    finished = executions.filter(duration_ms__isnull=False)
    avg_duration = finished.aggregate(models.Avg('duration_ms'))['duration_ms__avg'] or 0
    
    return JsonResponse({
        'workflow_id': workflow_id,
        'stats': {
            'total_executions': total,
            'success': success,
            'error': error,
            'pending': pending,
            'avg_duration_ms': round(avg_duration, 2)
        }
    })


def trigger_n8n_event(trigger_type, data, user=None):
    """
    Helper funkcia pre triggrovanie n8n workflows z kódu
    
    Použitie:
        from n8n_integration.views import trigger_n8n_event
        trigger_n8n_event('scan', {'qr_code': 'ABC123', 'user_id': 1})
    """
    triggers = N8nTrigger.objects.filter(
        trigger_type=trigger_type,
        is_active=True
    )
    
    results = []
    
    for trigger in triggers:
        workflow = trigger.workflow
        
        if not workflow.is_active or not workflow.webhook_url:
            continue
        
        # Overiť podmienky ak existujú
        if trigger.conditions:
            # Tu môžeš implementovať logiku pre podmienky
            pass
        
        # Pridať metadata
        payload = {
            'trigger_type': trigger_type,
            'data': data,
            '_metadata': {
                'trigger_id': trigger.id,
                'trigger_name': trigger.name,
                'triggered_at': timezone.now().isoformat(),
                'user_id': user.id if user else None,
            }
        }
        
        # Zaznamenať execution
        execution_log = N8nExecutionLog.objects.create(
            workflow=workflow,
            request_data=payload,
            status='running',
            user=user
        )
        
        try:
            response = requests.post(
                workflow.webhook_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                execution_log.mark_success(response.json() if response.headers.get('content-type', '').startswith('application/json') else {'raw': response.text})
                trigger.increment_count()
                results.append({'trigger': trigger.name, 'status': 'success'})
            else:
                execution_log.mark_error(f"HTTP {response.status_code}")
                results.append({'trigger': trigger.name, 'status': 'error', 'code': response.status_code})
                
        except Exception as e:
            execution_log.mark_error(str(e))
            results.append({'trigger': trigger.name, 'status': 'error', 'error': str(e)})
    
    return results
