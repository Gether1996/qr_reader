from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from qr_reader_django import crud
import json
from qr_reader_django.audit import get_client_ip

def create_qr_code(request):
    """Create a new QR code (company or manager with permission)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get company
            if is_company:
                company = crud.get_company_by_id(request.session['company_id'])
            else:
                user = crud.get_user_by_id(request.session['user_id'])
                if not user or not user.is_manager or not user.can_edit_qr_codes:
                    return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
                company = user.company
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            # Extract actor info for audit logging
            if is_company:
                actor_type = 'company'
                actor_email = company.email
                actor_name = company.name
            else:
                actor_type = 'user'
                actor_email = user.email
                actor_name = user.name
            
            qr_code, error = crud.create_qr_code(
                company=company,
                name=data.get('name'),
                location=data.get('location'),
                additional_info=data.get('additional_info', ''),
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request)
            )
            
            if error:
                return JsonResponse({'status': 'error', 'message': error}, status=400)
            
            return JsonResponse({
                'status': 'success',
                'message': str(_('QR code created successfully')),
                'qr_code_id': qr_code.id,
                'uuid': qr_code.uuid
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)


def delete_qr_code(request, qr_id):
    """Delete/deactivate a QR code (company or manager with permission)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)
    
    # Get company
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
    else:
        user = crud.get_user_by_id(request.session['user_id'])
        if not user or not user.is_manager or not user.can_edit_qr_codes:
            return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
        company = user.company
    
    if not company:
        return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
    
    # Extract actor info for audit logging
    if is_company:
        actor_type = 'company'
        actor_email = company.email
        actor_name = company.name
    else:
        actor_type = 'user'
        actor_email = user.email
        actor_name = user.name
    
    success, error = crud.deactivate_qr_code(
        qr_id, 
        company,
        actor_type=actor_type,
        actor_email=actor_email,
        actor_name=actor_name,
        ip_address=get_client_ip(request)
    )
    if success:
        return JsonResponse({
            'status': 'success',
            'message': str(_('QR code deactivated successfully'))
        })

    return JsonResponse({'status': 'error', 'message': error or str(_('Failed to deactivate QR code'))}, status=404)
