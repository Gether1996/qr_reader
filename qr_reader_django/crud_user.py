from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from qr_reader_django import crud
from viewer.account_texts import get_employee_invite_texts, get_user_password_setup_texts
from viewer.email_utils import get_email_language_code, render_localized_email
from viewer.models import UserPasswordSetupToken
import json
import secrets
from datetime import datetime, timedelta
from qr_reader_django.audit import get_client_ip


def _password_has_required_policy(password):
    return len(password) >= 10 and any(char.isupper() for char in password)


def _build_user_setup_url(request, token):
    scheme = request.scheme
    host = request.get_host()
    language_code = get_email_language_code(request=request)
    return f"{scheme}://{host}/{language_code}/user/set-password/{token}/"


def _get_combined_password_message(language_code):
    language = (language_code or 'en').split('-')[0].lower()
    messages = {
        'sk': 'Vyplnte obe polia hesla alebo ich nechajte prazdne a odosleme email s linkom na nastavenie hesla.',
        'de': 'Fuellen Sie beide Passwortfelder aus oder lassen Sie sie leer, damit wir einen Link zum Festlegen des Passworts per E-Mail senden koennen.',
        'es': 'Rellena ambos campos de contrasena o dejalos vacios para enviar un enlace de configuracion por correo.',
        'en': 'Fill both password fields or leave them blank to send a password setup link by email.',
    }
    return messages.get(language, messages['en'])

def create_user(request):
    """Register a new user under the company (company or manager with permission)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = (data.get('password') or '').strip()
            password_confirm = (data.get('password_confirm') or '').strip()
            language_code = get_email_language_code(request=request)
            invite_texts = get_employee_invite_texts(language_code)
            setup_texts = get_user_password_setup_texts(language_code)
            is_invite_flow = not password and not password_confirm

            if (password and not password_confirm) or (password_confirm and not password):
                return JsonResponse({
                    'status': 'error',
                    'message': _get_combined_password_message(getattr(request, 'LANGUAGE_CODE', 'en'))
                }, status=400)

            if password and password != password_confirm:
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('Passwords do not match'))
                }, status=400)

            if password and not _password_has_required_policy(password):
                return JsonResponse({
                    'status': 'error',
                    'message': f"{setup_texts['password_length_error']} {setup_texts['password_uppercase_error']}"
                }, status=400)
            
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

            with transaction.atomic():
                user, error = crud.create_user(
                    company=company,
                    name=data.get('name'),
                    email=data.get('email'),
                    password=password,
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
                    rc=data.get('rc'),
                    phone=data.get('phone'),
                    birth_date=data.get('birth_date'),
                    actor_type=actor_type,
                    actor_email=actor_email,
                    actor_name=actor_name,
                    ip_address=get_client_ip(request)
                )

                if error:
                    return JsonResponse({'status': 'error', 'message': error}, status=400)

                response_message = str(_('User created successfully'))

                if is_invite_flow:
                    UserPasswordSetupToken.objects.filter(user=user, is_used=False).update(is_used=True)
                    setup_token = secrets.token_urlsafe(48)
                    expires_at = datetime.now() + timedelta(hours=24)

                    UserPasswordSetupToken.objects.create(
                        user=user,
                        token=setup_token,
                        expires_at=expires_at
                    )

                    setup_url = _build_user_setup_url(request, setup_token)
                    email_html, _render_language = render_localized_email('user_password_setup_email.html', {
                        'company_name': company.name,
                        'company_email': company.email,
                        'user_name': user.name,
                        'user_email': user.email,
                        'setup_url': setup_url,
                        'request_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'copy': invite_texts,
                    }, language_code=language_code, request=request)

                    send_mail(
                        subject=invite_texts['subject'],
                        message=f"{invite_texts['button_label']}: {setup_url}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=email_html,
                        fail_silently=False
                    )

                    response_message = invite_texts['success_message']
            
            return JsonResponse({
                'status': 'success',
                'message': response_message,
                'invite_sent': is_invite_flow,
                'user_id': user.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': invite_texts['send_failed_message'] if 'invite_texts' in locals() and is_invite_flow else str(e)
            }, status=400)

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
                rc=data.get('rc'),
                phone=data.get('phone'),
                birth_date=data.get('birth_date'),
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
