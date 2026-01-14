from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _, activate
from django.conf import settings
from qr_reader_django import crud
import json
from viewer.models import Vacation
from qr_reader_django.audit import log_action, get_client_ip
from django.core.mail import send_mail
from django.template.loader import render_to_string

def create_vacation(request):
    """Create a new vacation (company, manager, or user for themselves)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_user = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_user):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get company and current user
            if is_company:
                company = crud.get_company_by_id(request.session['company_id'])
                current_user = None
            else:  # is_user (regular user or manager)
                current_user = crud.get_user_by_id(request.session['user_id'])
                if not current_user:
                    return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
                company = current_user.company
                
                # Check if manager has permission to edit absences
                if current_user.is_manager and not current_user.can_edit_absences:
                    # Manager without permission can only create for themselves
                    if data.get('user_id') != current_user.id:
                        return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            # Determine target user
            target_user_id = data.get('user_id')
            
            # Regular users can only create vacations for themselves
            if is_user and not is_company:
                if current_user.is_manager and current_user.can_edit_absences:
                    # Manager with permission can create for anyone in company
                    user = crud.get_user_by_id(target_user_id)
                else:
                    # Regular user or manager without permission can only create for themselves
                    user = current_user
            else:
                # Company can create for anyone
                user = crud.get_user_by_id(target_user_id)
            
            if not user or user.company != company:
                return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
            
            # Set approved=True if created by company or manager with permission, False otherwise
            approved = is_company or (current_user and current_user.is_manager and current_user.can_edit_absences)
            
            # Extract actor info for audit logging
            if is_company:
                actor_type = 'company'
                actor_email = company.email
                actor_name = company.name
            else:
                actor_type = 'user'
                actor_email = current_user.email
                actor_name = current_user.name
            
            vacation, error = crud.create_vacation(
                user=user,
                date_from=data.get('date_from'),
                date_to=data.get('date_to'),
                time_from=data.get('time_from'),
                time_to=data.get('time_to'),
                vacation_type=data.get('type', 'vacation'),
                approved=approved,
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request),
                request=request
            )
            
            if error:
                return JsonResponse({'status': 'error', 'message': error}, status=400)
            
            return JsonResponse({
                'status': 'success',
                'message': str(_('Vacation created successfully')),
                'vacation_id': vacation.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)


def edit_vacation(request, vacation_id):
    """Edit vacation details (company, manager with permission, or user editing their own)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_user = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_user):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get company and current user
            if is_company:
                company = crud.get_company_by_id(request.session['company_id'])
                current_user = None
            else:  # is_user
                current_user = crud.get_user_by_id(request.session['user_id'])
                if not current_user:
                    return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
                company = current_user.company
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            # Get the vacation to check ownership
            try:
                vacation = Vacation.objects.get(id=vacation_id, user__company=company)
            except Vacation.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': str(_('Vacation not found'))}, status=404)
            
            # Check permissions
            if is_user and not is_company:
                # Regular user can only edit their own vacations
                if current_user.is_manager and current_user.can_edit_absences:
                    # Manager with permission can edit anyone's vacation
                    pass
                elif vacation.user != current_user:
                    # Regular user or manager without permission can only edit their own
                    return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
            
            # Extract actor info for audit logging
            if is_company:
                actor_type = 'company'
                actor_email = company.email
                actor_name = company.name
            else:
                actor_type = 'user'
                actor_email = current_user.email
                actor_name = current_user.name
            
            vacation, error = crud.update_vacation(
                vacation_id=vacation_id,
                company=company,
                user_id=data.get('user_id'),
                date_from=data.get('date_from'),
                date_to=data.get('date_to'),
                time_from=data.get('time_from'),
                time_to=data.get('time_to'),
                vacation_type=data.get('type'),
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request)
            )
            
            if error:
                return JsonResponse({'status': 'error', 'message': error}, status=400)
            
            return JsonResponse({
                'status': 'success',
                'message': str(_('Vacation updated successfully'))
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)


def delete_vacation(request, vacation_id):
    """Delete vacation (company, manager with permission, or user deleting their own)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_user = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_user):
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            # Get company and current user
            if is_company:
                company = crud.get_company_by_id(request.session['company_id'])
                current_user = None
            else:  # is_user
                current_user = crud.get_user_by_id(request.session['user_id'])
                if not current_user:
                    return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
                company = current_user.company
            
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            # Get the vacation to check ownership
            try:
                vacation = Vacation.objects.get(id=vacation_id, user__company=company)
            except Vacation.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': str(_('Vacation not found'))}, status=404)
            
            # Check permissions
            if is_user and not is_company:
                # Regular user can only delete their own vacations
                if current_user.is_manager and current_user.can_edit_absences:
                    # Manager with permission can delete anyone's vacation
                    pass
                elif vacation.user != current_user:
                    # Regular user or manager without permission can only delete their own
                    return JsonResponse({'status': 'error', 'message': str(_('Access denied'))}, status=403)
            
            # Extract actor info for audit logging
            if is_company:
                actor_type = 'company'
                actor_email = company.email
                actor_name = company.name
            else:
                actor_type = 'user'
                actor_email = current_user.email
                actor_name = current_user.name
            
            # Check if user is deleting their own vacation
            is_self_delete = is_user and vacation.user == current_user
            
            success, error = crud.delete_vacation(
                vacation_id, 
                company,
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                ip_address=get_client_ip(request),
                request=request,
                is_self_delete=is_self_delete
            )
            
            if success:
                return JsonResponse({
                    'status': 'success',
                    'message': str(_('Vacation deleted successfully'))
                })
            else:
                return JsonResponse({'status': 'error', 'message': error}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def approve_vacation(request, vacation_id):
    """Approve vacation (company or manager with can_edit_absences permission)"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_user = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_user):
        # If not logged in, redirect to login
        if request.method == 'GET':
            from django.shortcuts import redirect
            return redirect('company_login')
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    # Get company and current user
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
        can_approve = True
        actor_type = 'company'
        actor_email = company.email
        actor_name = company.name
    else:  # is_user
        current_user = crud.get_user_by_id(request.session['user_id'])
        if not current_user:
            if request.method == 'GET':
                from django.shortcuts import redirect
                return redirect('company_login')
            return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
        company = current_user.company
        # Check if user is manager with can_edit_absences permission
        can_approve = current_user.is_manager and current_user.can_edit_absences
        actor_type = 'user'
        actor_email = current_user.email
        actor_name = current_user.name
    
    if not company:
        if request.method == 'GET':
            from django.shortcuts import redirect
            return redirect('company_login')
        return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
    
    if not can_approve:
        if request.method == 'GET':
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, str(_('Access denied. Only company or managers with edit absences permission can approve.')))
            return redirect('company_dashboard')
        return JsonResponse({'status': 'error', 'message': str(_('Access denied. Only company or managers with edit absences permission can approve.'))}, status=403)
    
    # Get the vacation
    try:
        vacation = Vacation.objects.get(id=vacation_id, user__company=company)
    except Vacation.DoesNotExist:
        if request.method == 'GET':
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, str(_('Vacation not found')))
            return redirect('company_dashboard')
        return JsonResponse({'status': 'error', 'message': str(_('Vacation not found'))}, status=404)
    
    # Check if already approved
    if vacation.approved:
        if request.method == 'GET':
            from django.shortcuts import redirect
            from django.contrib import messages
            from urllib.parse import quote
            messages.info(request, str(_('This vacation request has already been approved.')))
            return redirect(f'/company/dashboard/?tab=absences&name={quote(vacation.user.name)}')
        return JsonResponse({'status': 'success', 'message': str(_('Vacation already approved'))})

    # Set approved to True
    vacation.approved = True
    vacation.save()
            
    # Send email notification to the employee
    try:
        # Build dashboard URL from request
        if hasattr(request, 'build_absolute_uri'):
            dashboard_url = request.build_absolute_uri('/user/dashboard/')
        else:
            dashboard_url = '#'
        
        # Get language code from request
        language_code = request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else 'sk'
        
        # Calculate days count
        days_count = (vacation.date_to - vacation.date_from).days + 1
        
        # Prepare email context
        email_context = {
            'vacation_type': vacation.type,
            'user_name': vacation.user.name,
            'date_from': vacation.date_from,
            'date_to': vacation.date_to,
            'days_count': days_count,
            'approved': True,
            'cancelled': False,
            'company_name': company.name,
            'dashboard_url': dashboard_url,
            'LANGUAGE_CODE': language_code
        }
        
        # Activate language for translations
        activate(language_code)
        
        # Render email HTML
        html_message = render_to_string('vacation_notification.html', email_context, request=request)
        
        # Email subject
        subject = f'✅ {_("Vacation Request Approved")} - {vacation.date_from.strftime("%d.%m.%Y")} - {vacation.date_to.strftime("%d.%m.%Y")}'
        
        # Send email to employee
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[vacation.user.email],
            html_message=html_message,
            fail_silently=True
        )
    except Exception as e:
        # Log error but don't fail the approval
        print(f"Failed to send approval notification email: {str(e)}")
    
    # Log approval action
    log_action(
        actor_type=actor_type,
        actor_email=actor_email,
        actor_name=actor_name,
        action='approve',
        message=f'Approved vacation for {vacation.user.name} ({vacation.date_from} to {vacation.date_to})',
        ip_address=get_client_ip(request)
    )
    
    # Handle response based on request method
    if request.method == 'GET':
        from django.shortcuts import redirect
        from django.contrib import messages
        from urllib.parse import quote
        messages.success(request, str(_('Vacation approved successfully')))
        return redirect(f'/company/dashboard/?tab=absences&name={quote(vacation.user.name)}')
    else:  # POST
        return JsonResponse({
            'status': 'success',
            'message': str(_('Vacation approved successfully'))
        })