from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from qr_reader_django import crud
import json
from qr_reader_django.audit import get_client_ip

def create_user(request):
    """Register a new user under the company (company or manager with permission)"""
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
                if not user or not user.is_manager or not user.can_edit_employees:
                    return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
                company = user.company
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            # Get actor info
            if is_company:
                actor_type, actor_email, actor_name = 'company', company.email, company.name
            else:
                actor_type, actor_email, actor_name = 'user', user.email, user.name
            
            user, error = crud.create_user(
                company=company,
                name=data.get('name'),
                email=data.get('email'),
                password=data.get('password'),
                basic_work_hours=data.get('basic_work_hours', 160),
                holidays_per_year=data.get('holidays_per_year', 20),
                has_lunch_break=data.get('has_lunch_break', True),
                lunch_break_duration=data.get('lunch_break_duration', 30),
                is_manager=data.get('is_manager', False),
                can_edit_employees=data.get('can_edit_employees', False),
                can_edit_qr_codes=data.get('can_edit_qr_codes', False),
                can_edit_absences=data.get('can_edit_absences', False),
                notify_arrival=data.get('notify_arrival', False),
                notify_departure=data.get('notify_departure', False),
                notify_vacation=data.get('notify_vacation', False),
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request)
            )
            
            if error:
                return JsonResponse({'status': 'error', 'message': error}, status=400)
            
            return JsonResponse({
                'status': 'success',
                'message': str(_('User created successfully')),
                'user_id': user.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)


def edit_user(request, user_id):
    """Edit user details (company or manager with permission)"""
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
                current_user = crud.get_user_by_id(request.session['user_id'])
                if not current_user or not current_user.is_manager or not current_user.can_edit_employees:
                    return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
                company = current_user.company
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            user = crud.get_user_by_id(user_id)
            if not user or user.company != company:
                return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
            
            data = json.loads(request.body)
            
            # Extract actor info for audit logging
            if is_company:
                actor_type = 'company'
                actor_email = company.email
                actor_name = company.name
            else:
                manager = crud.get_user_by_id(request.session['user_id'])
                actor_type = 'user'
                actor_email = manager.email
                actor_name = manager.name
            
            user, error = crud.update_user(
                user_id=user_id,
                company=company,
                name=data.get('name'),
                email=data.get('email'),
                password=data.get('password'),
                basic_work_hours=data.get('basic_work_hours'),
                holidays_per_year=data.get('holidays_per_year'),
                has_lunch_break=data.get('has_lunch_break'),
                lunch_break_duration=data.get('lunch_break_duration'),
                is_active=data.get('is_active'),
                is_manager=data.get('is_manager'),
                can_edit_employees=data.get('can_edit_employees'),
                can_edit_qr_codes=data.get('can_edit_qr_codes'),
                can_edit_absences=data.get('can_edit_absences'),
                notify_arrival=data.get('notify_arrival'),
                notify_departure=data.get('notify_departure'),
                notify_vacation=data.get('notify_vacation'),
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request)
            )
            
            if error:
                return JsonResponse({'status': 'error', 'message': error}, status=400)
            
            return JsonResponse({
                'status': 'success',
                'message': str(_('User updated successfully'))
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)


def delete_user(request, user_id):
    """Delete user (company or manager with permission)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            # Get company
            if is_company:
                company = crud.get_company_by_id(request.session['company_id'])
            else:
                current_user = crud.get_user_by_id(request.session['user_id'])
                if not current_user or not current_user.is_manager or not current_user.can_edit_employees:
                    return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
                company = current_user.company
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            user = crud.get_user_by_id(user_id)
            if not user or user.company != company:
                return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
            
            # Extract actor info for audit logging
            if is_company:
                actor_type = 'company'
                actor_email = company.email
                actor_name = company.name
            else:
                manager = crud.get_user_by_id(request.session['user_id'])
                actor_type = 'user'
                actor_email = manager.email
                actor_name = manager.name
            
            success, error = crud.delete_user(
                user_id, 
                company,
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request)
            )
            
            if success:
                return JsonResponse({
                    'status': 'success',
                    'message': str(_('User deleted successfully'))
                })
            else:
                return JsonResponse({'status': 'error', 'message': error}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)