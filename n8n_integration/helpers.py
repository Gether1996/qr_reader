"""
Helper funkcie pre n8n integráciu

Tento modul poskytuje pomocné funkcie pre prácu s n8n workflows
"""

import requests
from django.conf import settings
from .models import N8nWorkflow, N8nExecutionLog


def send_to_n8n(workflow_id, data, user=None):
    """
    Pošle data do n8n workflow
    
    Args:
        workflow_id (str): ID workflow v databáze
        data (dict): Data na odoslanie
        user (User): Používateľ ktorý triggeruje workflow (voliteľné)
    
    Returns:
        dict: Response z n8n alebo error
    
    Example:
        from n8n_integration.helpers import send_to_n8n
        
        result = send_to_n8n(
            workflow_id='scan-notification',
            data={'scan_id': 123, 'user': 'John Doe'},
            user=request.user
        )
    """
    try:
        workflow = N8nWorkflow.objects.get(workflow_id=workflow_id, is_active=True)
        
        if not workflow.webhook_url:
            return {'error': 'Workflow nemá nakonfigurovanú webhook URL'}
        
        execution_log = N8nExecutionLog.objects.create(
            workflow=workflow,
            request_data=data,
            status='running',
            user=user
        )
        
        response = requests.post(
            workflow.webhook_url,
            json=data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            response_data = response.json() if 'application/json' in response.headers.get('content-type', '') else {'raw': response.text}
            execution_log.mark_success(response_data)
            return {'success': True, 'data': response_data, 'execution_id': execution_log.id}
        else:
            execution_log.mark_error(f"HTTP {response.status_code}")
            return {'error': f"HTTP {response.status_code}", 'details': response.text}
            
    except N8nWorkflow.DoesNotExist:
        return {'error': f'Workflow {workflow_id} neexistuje'}
    except Exception as e:
        if 'execution_log' in locals():
            execution_log.mark_error(str(e))
        return {'error': str(e)}


def trigger_on_scan(scan_event):
    """
    Automaticky trigger workflow pri QR scan evente
    
    Args:
        scan_event: ScanEvent model instance
    
    Example:
        from n8n_integration.helpers import trigger_on_scan
        
        # V views.py po vytvorení scan eventu:
        scan = ScanEvent.objects.create(...)
        trigger_on_scan(scan)
    """
    from .views import trigger_n8n_event
    
    data = {
        'scan_id': scan_event.id,
        'qr_code': scan_event.qr_code.code if scan_event.qr_code else None,
        'user_id': scan_event.user.id if scan_event.user else None,
        'timestamp': scan_event.timestamp.isoformat(),
        'address': scan_event.address,
        'scan_type': scan_event.scan_type,
    }
    
    return trigger_n8n_event('scan', data, user=scan_event.user)


def trigger_on_vacation_request(vacation):
    """
    Automaticky trigger workflow pri žiadosti o dovolenku
    
    Args:
        vacation: Vacation model instance
    
    Example:
        from n8n_integration.helpers import trigger_on_vacation_request
        
        vacation = Vacation.objects.create(...)
        trigger_on_vacation_request(vacation)
    """
    from .views import trigger_n8n_event
    
    data = {
        'vacation_id': vacation.id,
        'user_id': vacation.user.id,
        'user_name': f"{vacation.user.first_name} {vacation.user.last_name}",
        'start_date': vacation.start_date.isoformat(),
        'end_date': vacation.end_date.isoformat(),
        'vacation_type': vacation.type,
        'is_approved': vacation.is_approved,
    }
    
    return trigger_n8n_event('vacation_request', data, user=vacation.user)


def trigger_on_user_register(user, company):
    """
    Automaticky trigger workflow pri registrácii používateľa
    
    Args:
        user: User model instance
        company: Company info
    
    Example:
        from n8n_integration.helpers import trigger_on_user_register
        
        user = User.objects.create(...)
        trigger_on_user_register(user, company_obj)
    """
    from .views import trigger_n8n_event
    
    data = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'company': company,
        'registered_at': user.date_joined.isoformat(),
    }
    
    return trigger_n8n_event('user_register', data, user=user)


def trigger_on_magazine_publish(magazine):
    """
    Automaticky trigger workflow pri publikácii magazínu
    
    Args:
        magazine: Magazine model instance
    
    Example:
        from n8n_integration.helpers import trigger_on_magazine_publish
        
        magazine = Magazine.objects.create(...)
        trigger_on_magazine_publish(magazine)
    """
    from .views import trigger_n8n_event
    
    data = {
        'magazine_id': magazine.id,
        'title': magazine.title,
        'description': magazine.description,
        'created_at': magazine.created_at.isoformat(),
        'articles_count': magazine.articles.count(),
    }
    
    return trigger_n8n_event('magazine_publish', data)


# Konštanty pre n8n konfiguráciu
N8N_BASE_URL = getattr(settings, 'N8N_URL', 'http://n8n:5678')
N8N_API_KEY = getattr(settings, 'N8N_API_KEY', '')
