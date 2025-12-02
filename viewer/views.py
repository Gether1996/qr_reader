from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from qr_reader_django import crud
import json
from viewer.models import ScanEvent
from django.core.paginator import Paginator
import datetime

# ============= PUBLIC VIEWS =============

def landing_page(request):
    """Landing page with links to company and user login"""
    return render(request, 'landing.html')


def scan_qr(request, uuid):
    """Public page for scanning QR codes - logs location and timestamp"""
    qr_code = crud.get_qr_code_by_uuid(uuid)
    if not qr_code:
        messages.error(request, _('QR code not found or inactive'))
        return redirect('landing_page')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            scan_type = data.get('scan_type', 'arrival')
            device_info = data.get('device_info', '')

            # Get user if logged in
            user = None
            if 'user_id' in request.session:
                user = crud.get_user_by_id(request.session['user_id'])

            scan, address = crud.create_scan_event(
                qr_code=qr_code,
                latitude=latitude,
                longitude=longitude,
                scan_type=scan_type,
                scanned_by=user,
                device_info=device_info
            )
            
            return JsonResponse({'status': 'success', 'message': str(_('Scan recorded successfully!'))})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return render(request, 'scan_qr.html', {'qr_code': qr_code})


# ============= COMPANY AUTH VIEWS =============

def company_register(request):
    """Company registration page"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not all([name, email, password, confirm_password]):
            messages.error(request, _('All fields are required'))
            return render(request, 'company_register.html')

        if password != confirm_password:
            messages.error(request, _('Passwords do not match'))
            return render(request, 'company_register.html')

        company, error = crud.create_company(name, email, password)
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
            messages.success(request, f'Welcome back, {company.name}!')
            return redirect('company_dashboard')
        else:
            messages.error(request, _('Invalid credentials'))

    return render(request, 'company_login.html')


def company_logout(request):
    """Company logout"""
    request.session.flush()
    messages.success(request, _('Logged out successfully'))
    return redirect('landing_page')


def company_dashboard(request):
    """Company dashboard - manage QR codes and users"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company'))
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    qr_codes = crud.get_company_qr_codes(company)
    users = crud.get_company_users(company)
    recent_scans = crud.get_company_scans(company, limit=20)
    
    # Calculate arrivals and departures for each QR code
    for qr in qr_codes:
        qr.arrivals_count = qr.scans.filter(scan_type='arrival').count()
        qr.departures_count = qr.scans.filter(scan_type='departure').count()
    
    # Calculate total scans for each user (only from active QR codes)
    for user in users:
        user.total_scans = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__is_active=True
        ).count()

    context = {
        'company': company,
        'qr_codes': qr_codes,
        'users': users,
        'recent_scans': recent_scans,
    }
    return render(request, 'company_dashboard.html', context)


# ============= USER AUTH VIEWS =============

def user_login(request):
    """User login page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(f"USER LOGIN ATTEMPT - Email: {email}, DEBUG: {settings.DEBUG}")

        user = crud.get_user_by_email(email)
        print(f"User found: {user}, User active: {user.is_active if user else 'N/A'}")
        
        if user and user.check_password(password):
            print(f"Password check passed for user: {user.name}")
            request.session['user_id'] = user.id
            request.session['user_type'] = 'user'
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('user_dashboard')
        else:
            print(f"Login failed - User: {user}, Password check: {user.check_password(password) if user else 'N/A'}")
            messages.error(request, _('Invalid credentials'))

    return render(request, 'user_login.html')


def user_logout(request):
    """User logout"""
    request.session.flush()
    messages.success(request, _('Logged out successfully'))
    return redirect('landing_page')


def user_dashboard(request):
    if 'user_id' not in request.session or request.session.get('user_type') != 'user':
        messages.error(request, _('Please login as a user'))
        return redirect('user_login')

    user = crud.get_user_by_id(request.session['user_id'])
    if not user:
        messages.error(request, _('User not found'))
        return redirect('user_login')
    
    scans = ScanEvent.objects.filter(
        qr_code__company=user.company,
        scanned_by=user,
        qr_code__is_active=True
    ).select_related('qr_code', 'scanned_by')
    
    # Filtering
    qr_code_filter = request.GET.get('qr_code', '')
    scan_type_filter = request.GET.get('scan_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if qr_code_filter:
        scans = scans.filter(qr_code__name__icontains=qr_code_filter)
    
    if scan_type_filter:
        scans = scans.filter(scan_type=scan_type_filter)
    
    if date_from:
        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        scans = scans.filter(timestamp__date__gte=date_from_obj.date())
    
    if date_to:
        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        scans = scans.filter(timestamp__date__lte=date_to_obj.date())
    
    # Sorting - always default to DESC by timestamp if not specified
    sort_by = request.GET.get('sort', '-timestamp')
    valid_sort_fields = ['timestamp', '-timestamp', 'qr_code__name', '-qr_code__name', 
                         'scan_type', '-scan_type']
    
    if sort_by in valid_sort_fields:
        scans = scans.order_by(sort_by)
    else:
        scans = scans.order_by('-timestamp')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except:
        per_page = 20
    
    paginator = Paginator(scans, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Get unique QR codes for filter dropdown
    qr_codes = crud.get_company_qr_codes(user.company)
    
    # Check if any filters are active
    has_active_filters = any([qr_code_filter, scan_type_filter, date_from, date_to])

    context = {
        'user': user,
        'page_obj': page_obj,
        'qr_codes': qr_codes,
        'has_active_filters': has_active_filters,
        'current_filters': {
            'qr_code': qr_code_filter,
            'scan_type': scan_type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort_by,
            'per_page': per_page,
        }
    }
    return render(request, 'user_dashboard.html', context)


def user_scan_qr(request):
    """User QR scanner page"""
    if 'user_id' not in request.session or request.session.get('user_type') != 'user':
        messages.error(request, _('Please login as a user'))
        return redirect('user_login')

    user = crud.get_user_by_id(request.session['user_id'])
    if not user:
        messages.error(request, _('User not found'))
        return redirect('user_login')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uuid = data.get('uuid')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            scan_type = data.get('scan_type', 'arrival')
            
            # Check if QR code exists and belongs to user's company
            qr_code = crud.get_qr_code_by_uuid(uuid)
            
            if not qr_code:
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('QR code not found or inactive'))
                }, status=404)
            
            if qr_code.company != user.company:
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('This QR code does not belong to your company'))
                }, status=403)
            
            # Record the scan
            scan, address = crud.create_scan_event(
                qr_code=qr_code,
                scanned_by=user,
                latitude=latitude,
                longitude=longitude,
                scan_type=scan_type,
                device_info=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'status': 'success',
                'message': str(_('Scan recorded successfully!')),
                'data': {
                    'qr_name': qr_code.name,
                    'qr_location': qr_code.location,
                    'scan_timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'scan_latitude': latitude,
                    'scan_longitude': longitude,
                    'scan_address': address or str(_('Address not available'))
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    context = {
        'user': user,
    }
    return render(request, 'user_scan_qr.html', context)


# ============= COMPANY ACTIONS =============

def create_qr_code(request):
    """Create a new QR code (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            qr_code, error = crud.create_qr_code(
                company=company,
                name=data.get('name'),
                location=data.get('location'),
                additional_info=data.get('additional_info', '')
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
    """Delete/deactivate a QR code (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    success, error = crud.deactivate_qr_code(qr_id, company)
    if success:
        messages.success(request, _('QR code deactivated successfully'))
    else:
        messages.error(request, error or _('Failed to deactivate QR code'))
    
    return redirect('company_dashboard')


def create_user(request):
    """Register a new user under the company (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            user, error = crud.create_user(
                company=company,
                name=data.get('name'),
                email=data.get('email'),
                password=data.get('password')
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
    """Edit user details (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            data = json.loads(request.body)
            
            user, error = crud.update_user(
                user_id=user_id,
                company=company,
                name=data.get('name'),
                email=data.get('email'),
                password=data.get('password'),
                is_active=data.get('is_active')
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
    """Delete user (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            success, error = crud.delete_user(user_id, company)
            
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


def view_qr_scans(request, qr_id):
    """View all scans for a specific QR code with filtering and pagination"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    qr_code = crud.get_qr_code_by_id(qr_id, company)
    if not qr_code:
        messages.error(request, _('QR code not found'))
        return redirect('company_dashboard')
    
    scans = ScanEvent.objects.filter(qr_code=qr_code).select_related('qr_code', 'scanned_by')
    
    # Filtering
    user_filter = request.GET.get('user', '')
    scan_type_filter = request.GET.get('scan_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if user_filter:
        scans = scans.filter(scanned_by__name__icontains=user_filter)
    
    if scan_type_filter:
        scans = scans.filter(scan_type=scan_type_filter)
    
    if date_from:
        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        scans = scans.filter(timestamp__date__gte=date_from_obj.date())
    
    if date_to:
        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        scans = scans.filter(timestamp__date__lte=date_to_obj.date())
    
    # Sorting - always default to DESC by timestamp if not specified
    sort_by = request.GET.get('sort', '-timestamp')
    valid_sort_fields = ['timestamp', '-timestamp', 'scanned_by__name', '-scanned_by__name', 
                         'scan_type', '-scan_type']
    
    if sort_by in valid_sort_fields:
        scans = scans.order_by(sort_by)
    else:
        scans = scans.order_by('-timestamp')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except:
        per_page = 20
    
    paginator = Paginator(scans, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Check if any filters are active
    has_active_filters = any([user_filter, scan_type_filter, date_from, date_to])

    context = {
        'company': company,
        'qr_code': qr_code,
        'page_obj': page_obj,
        'has_active_filters': has_active_filters,
        'current_filters': {
            'user': user_filter,
            'scan_type': scan_type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort_by,
            'per_page': per_page,
        }
    }
    return render(request, 'qr_scans.html', context)


def view_user_details(request, user_id):
    """View detailed information about a specific user with filtering and pagination"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    user = crud.get_user_by_id(user_id)
    if not user or user.company != company:
        messages.error(request, _('User not found or inactive'))
        return redirect('company_dashboard')
    
    # Get all scans by this user
    scans = ScanEvent.objects.filter(scanned_by=user).select_related('qr_code', 'scanned_by')
    
    # Filtering
    qr_code_filter = request.GET.get('qr_code', '')
    scan_type_filter = request.GET.get('scan_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if qr_code_filter:
        scans = scans.filter(qr_code__name__icontains=qr_code_filter)
    
    if scan_type_filter:
        scans = scans.filter(scan_type=scan_type_filter)
    
    if date_from:
        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        scans = scans.filter(timestamp__date__gte=date_from_obj.date())
    
    if date_to:
        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d')
        scans = scans.filter(timestamp__date__lte=date_to_obj.date())
    
    # Sorting - always default to DESC by timestamp
    sort_by = request.GET.get('sort', '-timestamp')
    valid_sort_fields = ['timestamp', '-timestamp', 'qr_code__name', '-qr_code__name', 
                         'scan_type', '-scan_type']
    
    if sort_by in valid_sort_fields:
        scans = scans.order_by(sort_by)
    else:
        scans = scans.order_by('-timestamp')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except:
        per_page = 20
    
    paginator = Paginator(scans, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Check if any filters are active
    has_active_filters = any([qr_code_filter, scan_type_filter, date_from, date_to])

    context = {
        'company': company,
        'user': user,
        'page_obj': page_obj,
        'has_active_filters': has_active_filters,
        'current_filters': {
            'qr_code': qr_code_filter,
            'scan_type': scan_type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort_by,
            'per_page': per_page,
        }
    }
    return render(request, 'user_details.html', context)