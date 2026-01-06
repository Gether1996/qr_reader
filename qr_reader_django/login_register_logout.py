from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from qr_reader_django import crud
from qr_reader_django.audit import log_action, get_client_ip
from django.conf import settings

def company_register(request):
    """Company registration page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        auto_lunch_breaks = request.POST.get('auto_lunch_breaks') == 'on'
        
        # Notification preferences
        enable_notifications = request.POST.get('enable_notifications') == 'on'
        notify_arrival = enable_notifications and request.POST.get('notify_arrival') == 'on'
        notify_departure = enable_notifications and request.POST.get('notify_departure') == 'on'
        notify_vacation = enable_notifications and request.POST.get('notify_vacation') == 'on'

        if not all([name, email, password, confirm_password]):
            messages.error(request, _('All fields are required'))
            return render(request, 'company_register.html')

        if password != confirm_password:
            messages.error(request, _('Passwords do not match'))
            return render(request, 'company_register.html')

        company, error = crud.create_company(
            name, 
            email, 
            password, 
            auto_lunch_breaks=auto_lunch_breaks,
            notify_arrival=notify_arrival,
            notify_departure=notify_departure,
            notify_vacation=notify_vacation,
            ip_address=get_client_ip(request)
        )
        if error:
            messages.error(request, error)
            return render(request, 'company_register.html')

        messages.success(request, _('Company registered successfully! Please login.'))
        return redirect('company_login')

    return render(request, 'company_register.html')


def company_login(request):
    """Company login page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        company = crud.get_company_by_email(email)
        if company and company.check_password(password):
            request.session['company_id'] = company.id
            request.session['user_type'] = 'company'
            
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='login',
                message=f'Company "{company.name}" logged in',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, _('Welcome back, {}!').format(company.name))
            return redirect('company_dashboard')
        else:
            messages.error(request, _('Invalid credentials'))

    return render(request, 'company_login.html')


def company_logout(request):
    """Company logout"""
    if 'company_id' in request.session:
        company = crud.get_company_by_id(request.session['company_id'])
        if company:
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='logout',
                message=f'Company "{company.name}" logged out',
                ip_address=get_client_ip(request)
            )
    
    request.session.flush()
    messages.success(request, _('Logged out successfully'))
    return redirect('landing_page')

def user_login(request):
    """User login page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = crud.get_user_by_email(email)
        
        if user and user.check_password(password):
            # Check if already logged in (prevent duplicate login logs)
            already_logged_in = request.session.get('user_id') == user.id
            
            request.session['user_id'] = user.id
            request.session['user_type'] = 'user'
            
            # Only log if not already logged in
            if not already_logged_in:
                log_action(
                    actor_type='user',
                    actor_email=user.email,
                    actor_name=user.name,
                    action='login',
                    message=f'User "{user.name}" logged in',
                    ip_address=get_client_ip(request)
                )
            
            messages.success(request, _('Welcome back, {}!').format(user.name))
            return redirect('user_dashboard')
        else:
            messages.error(request, _('Invalid credentials'))

    return render(request, 'user_login.html')


def user_logout(request):
    """User logout"""
    if 'user_id' in request.session:
        user = crud.get_user_by_id(request.session['user_id'])
        if user:
            log_action(
                actor_type='user',
                actor_email=user.email,
                actor_name=user.name,
                action='logout',
                message=f'User "{user.name}" logged out',
                ip_address=get_client_ip(request)
            )
    
    request.session.flush()
    messages.success(request, _('Logged out successfully'))
    return redirect('landing_page')