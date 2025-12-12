from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from qr_reader_django import crud
import json
from viewer.models import ScanEvent, Vacation
from django.core.paginator import Paginator
from django.db.models import Q, Max
from django.views.decorators.csrf import csrf_exempt
import datetime
from django.utils.formats import date_format

# ============= PUBLIC VIEWS =============

def landing_page(request):
    """Landing page with links to company and user login"""
    # Redirect to dashboard if already logged in
    if 'company_id' in request.session and request.session.get('user_type') == 'company':
        return redirect('company_dashboard')
    elif 'user_id' in request.session and request.session.get('user_type') == 'user':
        return redirect('user_dashboard')
    
    return render(request, 'landing.html')


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
    """Company dashboard - manage QR codes, users, and absences"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company'))
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    # Get active tab from query params
    active_tab = request.GET.get('tab', 'qr-codes')
    
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    vacation_type = request.GET.get('vacation_type', '')
    user_filter = request.GET.get('user', '')
    absence_employee_name = request.GET.get('absence_employee_name', '')
    qr_name = request.GET.get('qr_name', '')
    employee_name = request.GET.get('employee_name', '')
    work_status = request.GET.get('work_status', '')
    items_per_page = request.GET.get('items_per_page', '25')
    sort = request.GET.get('sort', '')
    page_number = request.GET.get('page', 1)
    
    # Set default sorting based on active tab if not specified
    if not sort:
        if active_tab == 'qr-codes':
            sort = 'name'
        elif active_tab == 'users':
            sort = 'name'
        elif active_tab == 'absences':
            sort = '-date_from'
    
    # Validate items per page
    try:
        items_per_page = int(items_per_page)
        if items_per_page not in [10, 25, 50, 100]:
            items_per_page = 25
    except (ValueError, TypeError):
        items_per_page = 25
    
    # Get all QR codes for datalist (unfiltered)
    all_qr_codes = crud.get_company_qr_codes(company)
    
    # Get QR codes with filtering
    qr_codes = crud.get_company_qr_codes(company)
    if qr_name:
        qr_codes = qr_codes.filter(name__icontains=qr_name)
    
    # Apply sorting for QR codes (default: ASC on name)
    if active_tab == 'qr-codes':
        if sort:
            if sort == 'name':
                qr_codes = qr_codes.order_by('name')
            elif sort == '-name':
                qr_codes = qr_codes.order_by('-name')
            elif sort == 'created_at':
                qr_codes = qr_codes.order_by('created_at')
            elif sort == '-created_at':
                qr_codes = qr_codes.order_by('-created_at')
        else:
            # Default sort: ASC on name
            qr_codes = qr_codes.order_by('name')
    
    # Get all users for datalist (unfiltered)
    all_users = crud.get_company_users(company)
    
    # Get users with filtering
    users = crud.get_company_users(company)
    if employee_name:
        users = users.filter(name__icontains=employee_name)
    
    # Calculate arrivals and departures for each QR code and annotate scan count
    qr_codes_list = list(qr_codes)
    for qr in qr_codes_list:
        qr.arrivals_count = qr.scans.filter(scan_type='arrival').count()
        qr.departures_count = qr.scans.filter(scan_type='departure').count()
        qr.total_scans = qr.scans.count()
    
    # Apply sorting for QR codes (on scan count - requires list)
    if active_tab == 'qr-codes' and sort:
        if sort == 'scans':
            qr_codes_list.sort(key=lambda x: x.total_scans)
        elif sort == '-scans':
            qr_codes_list.sort(key=lambda x: x.total_scans, reverse=True)
    
    # Paginate QR codes
    if active_tab == 'qr-codes':
        qr_paginator = Paginator(qr_codes_list, items_per_page)
        qr_codes_page = qr_paginator.get_page(page_number)
    else:
        qr_codes_page = None
    
    # Calculate total scans for each user (only from active QR codes)
    # Store users as list to allow filtering by work status
    users_list = list(users)
    for user in users_list:
        user.total_scans = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__is_active=True
        ).count()
        
        # Get last scan to determine if user is at work
        last_scan = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__is_active=True
        ).order_by('-timestamp').first()
        
        if last_scan:
            user.is_at_work = last_scan.scan_type == 'arrival'
            user.work_location = last_scan.address if last_scan.address else f"{last_scan.latitude}, {last_scan.longitude}"
        else:
            user.is_at_work = False
            user.work_location = None
    
    # Apply work status filter
    if work_status:
        if work_status == 'at_work':
            users_list = [u for u in users_list if u.is_at_work]
        elif work_status == 'not_at_work':
            users_list = [u for u in users_list if not u.is_at_work]
    
    # Apply sorting for users (default: ASC on name)
    if active_tab == 'users':
        if sort:
            if sort == 'name':
                users_list.sort(key=lambda x: x.name.lower())
            elif sort == '-name':
                users_list.sort(key=lambda x: x.name.lower(), reverse=True)
            elif sort == 'scans':
                users_list.sort(key=lambda x: x.total_scans)
            elif sort == '-scans':
                users_list.sort(key=lambda x: x.total_scans, reverse=True)
            elif sort == 'at_work':
                users_list.sort(key=lambda x: x.is_at_work)
            elif sort == '-at_work':
                users_list.sort(key=lambda x: x.is_at_work, reverse=True)
        else:
            # Default sort: ASC on name
            users_list.sort(key=lambda x: x.name.lower())
    
    # Paginate users
    if active_tab == 'users':
        users_paginator = Paginator(users_list, items_per_page)
        users_page = users_paginator.get_page(page_number)
    else:
        users_page = None
    
    # Get absences for the company
    absences = Vacation.objects.filter(
        user__company=company,
        user__is_active=True
    ).select_related('user')
    
    # Apply filters to absences
    if date_from and date_to:
        try:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            # Filter absences that overlap with the selected date range
            # Absence overlaps if it starts before the end of range AND ends after the start of range
            absences = absences.filter(
                date_from__lte=date_to_obj,
                date_to__gte=date_from_obj
            )
        except ValueError:
            pass
    
    if vacation_type and vacation_type != 'all':
        absences = absences.filter(type=vacation_type)
    
    if user_filter:
        absences = absences.filter(user__id=user_filter)
    
    if absence_employee_name:
        absences = absences.filter(user__name__icontains=absence_employee_name)
    
    # Apply sorting for absences (default: DESC on date_from)
    if active_tab == 'absences':
        if sort:
            if sort == 'name':
                absences = absences.order_by('user__name')
            elif sort == '-name':
                absences = absences.order_by('-user__name')
            elif sort == 'date_from':
                absences = absences.order_by('date_from')
            elif sort == '-date_from':
                absences = absences.order_by('-date_from')
            elif sort == 'date_to':
                absences = absences.order_by('date_to')
            elif sort == '-date_to':
                absences = absences.order_by('-date_to')
            elif sort == 'type':
                absences = absences.order_by('type')
            elif sort == '-type':
                absences = absences.order_by('-type')
        else:
            # Default sort: DESC on date_from
            absences = absences.order_by('-date_from')
    
    # Paginate absences
    if active_tab == 'absences':
        absences_paginator = Paginator(absences, items_per_page)
        absences_page = absences_paginator.get_page(page_number)
    else:
        absences_page = None

    users_json = json.dumps([{'id': u.id, 'name': u.name} for u in all_users])     

    context = {
        'company': company,
        'all_qr_codes': all_qr_codes,  # All QR codes for datalist
        'qr_codes': qr_codes_list if active_tab == 'qr-codes' else [],
        'users': all_users,  # All users for datalist
        'users_json': users_json,
        'users_list': users_list if active_tab == 'users' else [],
        'absences': absences if active_tab == 'absences' else [],
        'qr_codes_page': qr_codes_page,
        'users_page': users_page,
        'absences_page': absences_page,
        'active_tab': active_tab,
        'current_filters': {
            'date_from': date_from,
            'date_to': date_to,
            'vacation_type': vacation_type,
            'user': user_filter,
            'absence_employee_name': absence_employee_name,
            'qr_name': qr_name,
            'employee_name': employee_name,
            'work_status': work_status,
            'items_per_page': str(items_per_page),
            'sort': sort,
        },
        'qr_codes_count': len(qr_codes_list),
        'users_count': len(users_list),
        'absences_count': absences.count(),
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
    
    # Get active tab from query parameter, default to 'scans'
    active_tab = request.GET.get('tab', 'scans')
    
    # Get unique QR codes for filter dropdown
    qr_codes = crud.get_company_qr_codes(user.company)
    qr_code_names = [qr.name for qr in qr_codes]
    
    # Shared filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', '-timestamp' if active_tab == 'scans' else '-date_from')
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except:
        per_page = 20
    
    # ===== SCANS TAB =====
    scans = ScanEvent.objects.filter(
        qr_code__company=user.company,
        scanned_by=user,
        qr_code__is_active=True
    ).select_related('qr_code', 'scanned_by')
    
    # Scans-specific filters
    qr_code_filter = request.GET.get('qr_code', '')
    scan_type_filter = request.GET.get('scan_type', '')
    
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
    
    # Sorting for scans
    valid_scan_sort_fields = ['timestamp', '-timestamp', 'qr_code__name', '-qr_code__name', 
                         'scan_type', '-scan_type']
    
    if active_tab == 'scans' and sort_by in valid_scan_sort_fields:
        scans = scans.order_by(sort_by)
    else:
        scans = scans.order_by('-timestamp')
    
    # Pagination for scans
    scans_paginator = Paginator(scans, per_page)
    page_obj = scans_paginator.get_page(page_number)
    scans_count = scans.count()
    
    # ===== ABSENCES TAB =====
    absences = Vacation.objects.filter(user=user).order_by('-date_from')
    
    # Absences-specific filters
    vacation_type_filter = request.GET.get('vacation_type', '')
    
    if vacation_type_filter:
        absences = absences.filter(type=vacation_type_filter)
    
    if date_from and date_to:
        date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
        absences = absences.filter(
            date_from__lte=date_to_obj,
            date_to__gte=date_from_obj
        )
    
    # Sorting for absences
    valid_absence_sort_fields = ['date_from', '-date_from', 'date_to', '-date_to', 
                                  'created_at', '-created_at']
    
    if active_tab == 'absences' and sort_by in valid_absence_sort_fields:
        absences = absences.order_by(sort_by)
    else:
        absences = absences.order_by('-date_from')
    
    # Pagination for absences
    absences_paginator = Paginator(absences, per_page)
    absences_page = absences_paginator.get_page(page_number)
    absences_count = absences.count()
    
    # Check if any filters are active
    has_active_filters = any([qr_code_filter, scan_type_filter, vacation_type_filter, date_from, date_to])

    context = {
        'user': user,
        'page_obj': page_obj,
        'absences_page': absences_page,
        'scans_count': scans_count,
        'absences_count': absences_count,
        'active_tab': active_tab,
        'qr_codes': qr_codes,
        'has_active_filters': has_active_filters,
        'datalist_items': qr_code_names,
        'current_filters': {
            'qr_code': qr_code_filter,
            'scan_type': scan_type_filter,
            'vacation_type': vacation_type_filter,
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
    
    # Get all users for datalist
    users = crud.get_company_users(company)
    user_names = [u.name for u in users]

    context = {
        'company': company,
        'qr_code': qr_code,
        'page_obj': page_obj,
        'has_active_filters': has_active_filters,
        'datalist_items': user_names,
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
    
    # Determine active tab
    active_tab = request.GET.get('tab', 'scans')
    
    # Filtering
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except:
        per_page = 20
    
    if active_tab == 'vacations':
        # Get all vacations by this user
        vacations = Vacation.objects.filter(user=user, is_active=True)
        
        # Additional filters for vacations
        vacation_type_filter = request.GET.get('vacation_type', '')
        
        if vacation_type_filter:
            vacations = vacations.filter(type=vacation_type_filter)
        
        # Date filter: show vacations that overlap with the date range
        if date_from and date_to:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            vacations = vacations.filter(
                date_from__lte=date_to_obj,
                date_to__gte=date_from_obj
            )
        elif date_from:
            date_from_obj = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            vacations = vacations.filter(date_to__gte=date_from_obj)
        elif date_to:
            date_to_obj = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
            vacations = vacations.filter(date_from__lte=date_to_obj)
        
        # Sorting - default to DESC by date_from
        sort_by = request.GET.get('sort', '-date_from')
        valid_sort_fields = ['date_from', '-date_from', 'date_to', '-date_to', 
                             'created_at', '-created_at']
        
        if sort_by in valid_sort_fields:
            vacations = vacations.order_by(sort_by)
        else:
            vacations = vacations.order_by('-date_from')
        
        # Pagination
        paginator = Paginator(vacations, per_page)
        vacations_page = paginator.get_page(page_number)
        
        # Check if any filters are active
        has_active_filters = any([date_from, date_to, vacation_type_filter])
        
        # Get counts
        scans_count = ScanEvent.objects.filter(scanned_by=user).count()
        vacations_count = Vacation.objects.filter(user=user).count()
        
        context = {
            'company': company,
            'user': user,
            'vacations_page': vacations_page,
            'page_obj': vacations_page,  # For paginator template
            'has_active_filters': has_active_filters,
            'active_tab': active_tab,
            'scans_count': scans_count,
            'vacations_count': vacations_count,
            'current_filters': {
                'date_from': date_from,
                'date_to': date_to,
                'vacation_type': vacation_type_filter,
                'sort': sort_by,
                'per_page': per_page,
            }
        }
    else:
        # Get all scans by this user
        scans = ScanEvent.objects.filter(scanned_by=user).select_related('qr_code', 'scanned_by')
        
        # Additional filters for scans
        qr_code_filter = request.GET.get('qr_code', '')
        scan_type_filter = request.GET.get('scan_type', '')
        
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
        paginator = Paginator(scans, per_page)
        page_obj = paginator.get_page(page_number)
        
        # Check if any filters are active
        has_active_filters = any([qr_code_filter, scan_type_filter, date_from, date_to])
        
        # Get all QR codes for datalist
        qr_codes = crud.get_company_qr_codes(company)
        qr_code_names = [qr.name for qr in qr_codes]
        
        # Get counts
        scans_count = ScanEvent.objects.filter(scanned_by=user).count()
        vacations_count = Vacation.objects.filter(user=user).count()

        context = {
            'company': company,
            'user': user,
            'page_obj': page_obj,
            'vacations_page': page_obj,  # Empty for scans tab
            'has_active_filters': has_active_filters,
            'datalist_items': qr_code_names,
            'active_tab': active_tab,
            'scans_count': scans_count,
            'vacations_count': vacations_count,
            'current_filters': {
                'qr_code': qr_code_filter,
                'scan_type': scan_type_filter,
                'date_from': date_from,
                'date_to': date_to,
                'sort': sort_by,
                'per_page': per_page,
            }
        }
    return render(request, 'company_user_details.html', context)

def create_vacation(request):
    """Create a new vacation (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            user = crud.get_user_by_id(data.get('user_id'))
            if not user or user.company != company:
                return JsonResponse({'status': 'error', 'message': str(_('User not found'))}, status=404)
            
            vacation, error = crud.create_vacation(
                user=user,
                date_from=data.get('date_from'),
                date_to=data.get('date_to'),
                vacation_type=data.get('type', 'vacation')
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
    """Edit vacation details (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            data = json.loads(request.body)
            
            vacation, error = crud.update_vacation(
                vacation_id=vacation_id,
                company=company,
                user_id=data.get('user_id'),
                date_from=data.get('date_from'),
                date_to=data.get('date_to'),
                vacation_type=data.get('type')
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
    """Delete vacation (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': str(_('Unauthorized'))}, status=403)

    if request.method == 'POST':
        try:
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': str(_('Company not found'))}, status=404)
            
            success, error = crud.delete_vacation(vacation_id, company)
            
            if success:
                return JsonResponse({
                    'status': 'success',
                    'message': str(_('Vacation deleted successfully'))
                })
            else:
                return JsonResponse({'status': 'error', 'message': error}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': str(_('Invalid method'))}, status=405)


def generate_attendance_pdf(request, user_id):
    """Generate PDF attendance report for a user"""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime, timedelta
    from collections import defaultdict
    import os
    
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')
    
    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    user = crud.get_user_by_id(user_id)
    if not user or user.company != company:
        messages.error(request, _('User not found'))
        return redirect('company_dashboard')
    
    # Parse date range - accept both date_range and date_from/date_to parameters
    date_range = request.GET.get('date_range', '')
    date_from_param = request.GET.get('date_from', '')
    date_to_param = request.GET.get('date_to', '')
    
    try:
        if date_from_param and date_to_param:
            # Use date_from and date_to parameters (format: YYYY-MM-DD)
            date_from = datetime.strptime(date_from_param, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_param, '%Y-%m-%d')
        elif date_range and ' - ' in date_range:
            # Use date_range parameter (format: DD.MM.YYYY - DD.MM.YYYY)
            date_from_str, date_to_str = date_range.split(' - ')
            date_from = datetime.strptime(date_from_str.strip(), '%d.%m.%Y')
            date_to = datetime.strptime(date_to_str.strip(), '%d.%m.%Y')
        else:
            messages.error(request, _('Invalid date range'))
            return redirect('view_user_details', user_id=user_id)
    except:
        messages.error(request, _('Invalid date format'))
        return redirect('view_user_details', user_id=user_id)
    
    # Get scans in date range
    scans = ScanEvent.objects.filter(
        scanned_by=user,
        timestamp__date__gte=date_from.date(),
        timestamp__date__lte=date_to.date()
    ).select_related('qr_code').order_by('timestamp')
    
    vacations = Vacation.objects.filter(
        user=user,
        is_active=True,
        date_from__lte=date_to.date(),
        date_to__gte=date_from.date()
    ).order_by('date_from')
    
    # Create directory structure for PDF storage
    now = datetime.now()
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'PDF', str(now.year), f"{now.month:02d}")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Generate filename
    filename = f"attendance_{user.name.replace(' ', '_')}_{date_from.strftime('%Y%m%d')}-{date_to.strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(pdf_dir, filename)
    
    # Register DejaVu fonts for Unicode support (Slovak characters)
    try:
        # Use fonts from project directory
        font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
        dejavu_path = os.path.join(font_dir, 'DejaVuSans.ttf')
        dejavu_bold_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
        
        if os.path.exists(dejavu_path) and os.path.exists(dejavu_bold_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold_path))
            font_name = 'DejaVuSans'
            font_name_bold = 'DejaVuSans-Bold'
        else:
            raise Exception("DejaVu fonts not found in project")
    except Exception as e:
        # Fallback to Helvetica if DejaVu is not available
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4), 
                           rightMargin=1*cm, leftMargin=1*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles with Unicode-compatible font
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=20,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name_bold,
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11
    )
    
    # Title
    elements.append(Paragraph(f"{_('Attendance Report')} - {user.name}", title_style))
    elements.append(Paragraph(f"{_('Period')}: {date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}", normal_style))
    elements.append(Paragraph(f"{_('Company')}: {company.name}", normal_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Group scans by day
    daily_data = defaultdict(list)
    for scan in scans:
        day = scan.timestamp.date()
        daily_data[day].append(scan)
    
    # Create dictionary of vacation days with type
    vacation_days = {}
    for vacation in vacations:
        current = vacation.date_from
        while current <= vacation.date_to:
            vacation_days[current] = vacation.type if vacation.type else 'vacation'
            current += timedelta(days=1)
    
    # Calculate statistics
    total_days = len(daily_data)
    total_work_hours = 0
    days_with_issues = []
    total_vacation_days = 0
    
    # Daily attendance table
    elements.append(Paragraph(str(_('Daily Attendance')), heading_style))
    
    # Use Paragraph objects for header cells to enable wrapping
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName=font_name_bold,
        fontSize=9,
        textColor=colors.whitesmoke,
        alignment=TA_CENTER,
        leading=11
    )
    
    table_data = [[
        Paragraph(str(_('Date')), header_style),
        Paragraph(str(_('Day')), header_style),
        Paragraph(str(_('Arrival')), header_style),
        Paragraph(str(_('Departure')), header_style),
        Paragraph(str(_('Hours')), header_style),
        Paragraph(str(_('Scanned QR')), header_style),
        Paragraph(str(_('Notes')), header_style)
    ]]
    
    # Style for data cells
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        leading=11
    )
    
    cell_style_centered = ParagraphStyle(
        'CellStyleCentered',
        parent=cell_style,
        alignment=TA_CENTER
    )
    
    current_date = date_from.date()
    while current_date <= date_to.date():
        day_scans = daily_data.get(current_date, [])
        # Use Django's date_format with 'l' format (day of the week)
        day_name = date_format(current_date, format='l')
        
        # Check if this day is a vacation day
        vacation_type = vacation_days.get(current_date)
        is_vacation = vacation_type is not None
        if is_vacation:
            total_vacation_days += 1
        
        if is_vacation and not day_scans:
            # Vacation day with no scans - display type
            if vacation_type == 'sick_leave':
                vacation_style = ParagraphStyle(
                    'SickLeaveStyle',
                    parent=cell_style,
                    textColor=colors.HexColor('#f59e0b'),
                    fontName=font_name_bold
                )
                leave_label = f"🏥 {_('Sick Leave')}"
            else:
                vacation_style = ParagraphStyle(
                    'VacationStyle',
                    parent=cell_style,
                    textColor=colors.HexColor('#10b981'),
                    fontName=font_name_bold
                )
                leave_label = f"🏖 {_('Vacation')}"
            
            table_data.append([
                Paragraph(current_date.strftime('%d.%m.%Y'), cell_style_centered),
                Paragraph(day_name, cell_style),
                Paragraph('-', cell_style_centered),
                Paragraph('-', cell_style_centered),
                Paragraph('-', cell_style_centered),
                Paragraph('-', cell_style),
                Paragraph(leave_label, vacation_style)
            ])
        elif not day_scans and not is_vacation:
            # No scans for this day
            table_data.append([
                Paragraph(current_date.strftime('%d.%m.%Y'), cell_style_centered),
                Paragraph(day_name, cell_style),
                Paragraph('-', cell_style_centered),
                Paragraph('-', cell_style_centered),
                Paragraph('0:00', cell_style_centered),
                Paragraph('-', cell_style),
                Paragraph(str(_('No scans')), cell_style)
            ])
        else:
            # Day with scans (may or may not be vacation)
            # Find arrivals and departures
            arrivals = [s for s in day_scans if s.scan_type == 'arrival']
            departures = [s for s in day_scans if s.scan_type == 'departure']
            
            # Check for issues
            notes = []
            
            # Special note if vacation day but has scans (data conflict)
            if is_vacation:
                if vacation_type == 'sick_leave':
                    notes.append(f"⚠ {_('Scans on sick leave day')}")
                else:
                    notes.append(f"⚠ {_('Scans on vacation day')}")
                days_with_issues.append(current_date)
            
            if not arrivals:
                notes.append(f"⚠ {_('Missing arrival')}")
                days_with_issues.append(current_date)
            if not departures:
                notes.append(f"⚠ {_('Missing departure')}")
                days_with_issues.append(current_date)
            
            # Calculate hours worked
            hours_worked = 0
            if arrivals and departures:
                first_arrival = arrivals[0].timestamp
                last_departure = departures[-1].timestamp
                work_duration = last_departure - first_arrival
                hours_worked = work_duration.total_seconds() / 3600
                total_work_hours += hours_worked
            
            # Get QR code info with location
            if arrivals:
                qr_info = f"{arrivals[0].qr_code.name}<br/><font size=8 color='#6b7280'>{arrivals[0].qr_code.location}</font>"
            elif departures:
                qr_info = f"{departures[0].qr_code.name}<br/><font size=8 color='#6b7280'>{departures[0].qr_code.location}</font>"
            else:
                qr_info = '-'
            
            # Format times
            arrival_time = arrivals[0].timestamp.strftime('%H:%M') if arrivals else '-'
            departure_time = departures[-1].timestamp.strftime('%H:%M') if departures else '-'
            hours_str = f"{int(hours_worked)}:{int((hours_worked % 1) * 60):02d}" if hours_worked > 0 else '0:00'
            
            # Use conflict style for notes if vacation conflict exists
            notes_style = cell_style
            if is_vacation:
                notes_style = ParagraphStyle(
                    'ConflictNotesStyle',
                    parent=cell_style,
                    textColor=colors.HexColor('#f59e0b')
                )
            
            table_data.append([
                Paragraph(current_date.strftime('%d.%m.%Y'), cell_style_centered),
                Paragraph(day_name, cell_style),
                Paragraph(arrival_time, cell_style_centered),
                Paragraph(departure_time, cell_style_centered),
                Paragraph(hours_str, cell_style_centered),
                Paragraph(qr_info, cell_style),
                Paragraph(' '.join(notes) if notes else '✓', notes_style)
            ])
        
        current_date += timedelta(days=1)
    
    # Create table - optimized column widths (A4 landscape is 29.7cm, minus 2cm margins = 27.7cm)
    table = Table(table_data, colWidths=[2.8*cm, 2.5*cm, 2*cm, 2*cm, 1.8*cm, 8.5*cm, 8.1*cm])
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, 0), 6),
        ('RIGHTPADDING', (0, 0), (-1, 0), 6),
        
        # Data rows styling
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 1), (-1, -1), 6),
        ('RIGHTPADDING', (0, 1), (-1, -1), 6),
        
        # Alignment for specific columns
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Day
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Arrival
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Departure
        ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Hours
        ('ALIGN', (5, 1), (5, -1), 'LEFT'),    # Location
        ('ALIGN', (6, 1), (6, -1), 'LEFT'),    # Notes
        
        # Grid and backgrounds
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e40af')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        
        # Border styling
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#6b7280')),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 1*cm))
    summary_elements = []
    summary_elements.append(Paragraph(str(_('Summary Statistics')), heading_style))
    
    avg_hours = total_work_hours / total_days if total_days > 0 else 0
    
    # Create styled summary label and value styles
    summary_label_style = ParagraphStyle(
        'SummaryLabel',
        parent=styles['Normal'],
        fontName=font_name_bold,
        fontSize=10,
        leading=13
    )
    
    summary_value_style = ParagraphStyle(
        'SummaryValue',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=13
    )
    
    # Create styled summary data
    summary_data = [
        [
            Paragraph(str(_('Total Working Days')), summary_label_style),
            Paragraph(str(total_days), summary_value_style)
        ],
        [
            Paragraph(str(_('Total Hours Worked')), summary_label_style),
            Paragraph(f"{int(total_work_hours)}:{int((total_work_hours % 1) * 60):02d}", summary_value_style)
        ],
        [
            Paragraph(str(_('Average Hours per Day')), summary_label_style),
            Paragraph(f"{int(avg_hours)}:{int((avg_hours % 1) * 60):02d}", summary_value_style)
        ],
        [
            Paragraph(str(_('Vacation Days')), summary_label_style),
            Paragraph(str(total_vacation_days), summary_value_style)
        ],
        [
            Paragraph(str(_('Days with Issues')), summary_label_style),
            Paragraph(str(len(set(days_with_issues))), summary_value_style)
        ],
    ]
    
    summary_table = Table(summary_data, colWidths=[10*cm, 7*cm])
    summary_table.setStyle(TableStyle([
        # Background colors
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        
        # Font styling
        ('FONTNAME', (0, 0), (0, -1), font_name_bold),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        
        # Alignment
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        
        # Grid styling
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#6b7280')),
        ('LINEAFTER', (0, 0), (0, -1), 1, colors.HexColor('#a5b4fc')),
    ]))
    
    summary_elements.append(summary_table)
    
    # Add summary as a single block that won't be split across pages
    elements.append(KeepTogether(summary_elements))
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response - serve from file
    with open(filepath, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


def generate_qr_code_pdf(request, qr_id):
    """Generate PDF with QR code for printing on A4"""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime
    import os
    
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')
    
    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    qr_code = crud.get_qr_code_by_id(qr_id)
    if not qr_code or qr_code.company != company:
        messages.error(request, _('QR Code not found'))
        return redirect('company_dashboard')
    
    # Create directory structure for PDF storage
    now = datetime.now()
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'PDF', str(now.year), f"{now.month:02d}")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Generate filename
    filename = f"qr_code_{qr_code.name.replace(' ', '_')}_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(pdf_dir, filename)
    
    # Register DejaVu fonts for Unicode support
    try:
        font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
        dejavu_path = os.path.join(font_dir, 'DejaVuSans.ttf')
        dejavu_bold_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
        
        if os.path.exists(dejavu_path) and os.path.exists(dejavu_bold_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold_path))
            font_name_bold = 'DejaVuSans-Bold'
        else:
            raise Exception("DejaVu fonts not found")
    except:
        font_name_bold = 'Helvetica-Bold'
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=3*cm, bottomMargin=3*cm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title style - centered
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30,
    )
    
    # Add title
    title = Paragraph(qr_code.name, title_style)
    elements.append(title)
    
    # Add spacer
    elements.append(Spacer(1, 2*cm))
    
    # Add QR code image - centered and larger
    qr_image_path = os.path.join(settings.MEDIA_ROOT, qr_code.qr_code.name)
    if os.path.exists(qr_image_path):
        # Create image with specific size (12cm x 12cm)
        img = Image(qr_image_path, width=12*cm, height=12*cm)
        img.hAlign = 'CENTER'
        elements.append(img)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response - open in new tab
    with open(filepath, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response


# ============= ANALYTICS VIEWS =============

def company_analytics(request):
    """Analytics dashboard with statistics and charts"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company'))
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login')
    
    from django.db.models import Count, Q, Max
    from django.utils import timezone
    from datetime import timedelta, datetime
    from calendar import monthrange
    
    today = timezone.now().date()
    
    # Get date range from request parameters
    date_from_param = request.GET.get('date_from')
    date_to_param = request.GET.get('date_to')
    
    # Parse custom date range or use defaults
    if date_from_param and date_to_param:
        try:
            date_from = datetime.strptime(date_from_param, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to_param, '%Y-%m-%d').date()
        except ValueError:
            date_from = today.replace(day=1)
            date_to = today
    else:
        # Default: current month (from 1st to today)
        date_from = today.replace(day=1)
        date_to = today
    
    week_ago = today - timedelta(days=7)
    
    # Current month (from 1st to today) - for secondary comparison
    current_month_start = today.replace(day=1)
    
    # Previous month (full calendar month) - for secondary comparison
    if today.month == 1:
        prev_month_start = today.replace(year=today.year - 1, month=12, day=1)
        prev_month_end = today.replace(year=today.year - 1, month=12, day=31)
    else:
        prev_month_start = today.replace(month=today.month - 1, day=1)
        days_in_prev_month = monthrange(prev_month_start.year, prev_month_start.month)[1]
        prev_month_end = prev_month_start.replace(day=days_in_prev_month)
    
    # Get all users and QR codes
    users = crud.get_company_users(company)
    qr_codes = crud.get_company_qr_codes(company)
    
    # Today's statistics (always based on actual today)
    today_scans = ScanEvent.objects.filter(
        qr_code__company=company,
        timestamp__date=today
    )
    today_arrivals = today_scans.filter(scan_type='arrival').count()
    today_departures = today_scans.filter(scan_type='departure').count()
    
    # Statistics for selected date range
    range_scans = ScanEvent.objects.filter(
        qr_code__company=company,
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    )
    range_arrivals = range_scans.filter(scan_type='arrival').count()
    range_departures = range_scans.filter(scan_type='departure').count()
    range_total_scans = range_scans.count()
    
    # Weekly statistics
    week_scans = ScanEvent.objects.filter(
        qr_code__company=company,
        timestamp__date__gte=week_ago
    ).count()
    
    # Current month statistics
    current_month_scans = ScanEvent.objects.filter(
        qr_code__company=company,
        timestamp__date__gte=current_month_start,
        timestamp__date__lte=today
    ).count()
    
    # Previous month statistics
    prev_month_scans = ScanEvent.objects.filter(
        qr_code__company=company,
        timestamp__date__gte=prev_month_start,
        timestamp__date__lte=prev_month_end
    ).count()
    
    # Currently in office (last scan was arrival)
    currently_in_office = []
    for user in users:
        last_scan = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__company=company
        ).order_by('-timestamp').first()
        
        if last_scan and last_scan.scan_type == 'arrival':
            currently_in_office.append({
                'user': user,
                'location': last_scan.qr_code.name,
                'time': last_scan.timestamp
            })
    
    # Top 5 most used QR codes (for selected date range)
    top_qr_codes = ScanEvent.objects.filter(
        qr_code__company=company,
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    ).values('qr_code__name', 'qr_code__location').annotate(
        scan_count=Count('id')
    ).order_by('-scan_count')[:5]
    
    # Calculate working hours for selected date range
    selected_range_work_hours = []
    for user in users:
        scans = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__company=company,
            timestamp__date__gte=date_from,
            timestamp__date__lte=date_to
        ).order_by('timestamp')
        
        total_hours = 0
        arrival_time = None
        
        for scan in scans:
            if scan.scan_type == 'arrival':
                arrival_time = scan.timestamp
            elif scan.scan_type == 'departure' and arrival_time:
                work_duration = (scan.timestamp - arrival_time).total_seconds() / 3600
                total_hours += work_duration
                arrival_time = None
        
        if total_hours > 0:  # Only include users with hours
            selected_range_work_hours.append({
                'user': user,
                'hours': round(total_hours, 1),
                'days': scans.values('timestamp__date').distinct().count()
            })
    
    # Calculate working hours for current month (calendar)
    current_month_work_hours = []
    for user in users:
        scans = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__company=company,
            timestamp__date__gte=current_month_start,
            timestamp__date__lte=today
        ).order_by('timestamp')
        
        total_hours = 0
        arrival_time = None
        
        for scan in scans:
            if scan.scan_type == 'arrival':
                arrival_time = scan.timestamp
            elif scan.scan_type == 'departure' and arrival_time:
                work_duration = (scan.timestamp - arrival_time).total_seconds() / 3600
                total_hours += work_duration
                arrival_time = None
        
        if total_hours > 0:  # Only include users with hours
            current_month_work_hours.append({
                'user': user,
                'hours': round(total_hours, 1),
                'days': scans.values('timestamp__date').distinct().count()
            })
    
    # Calculate working hours for previous month
    prev_month_work_hours = []
    for user in users:
        scans = ScanEvent.objects.filter(
            scanned_by=user,
            qr_code__company=company,
            timestamp__date__gte=prev_month_start,
            timestamp__date__lte=prev_month_end
        ).order_by('timestamp')
        
        total_hours = 0
        arrival_time = None
        
        for scan in scans:
            if scan.scan_type == 'arrival':
                arrival_time = scan.timestamp
            elif scan.scan_type == 'departure' and arrival_time:
                work_duration = (scan.timestamp - arrival_time).total_seconds() / 3600
                total_hours += work_duration
                arrival_time = None
        
        if total_hours > 0:  # Only include users with hours
            prev_month_work_hours.append({
                'user': user,
                'hours': round(total_hours, 1),
                'days': scans.values('timestamp__date').distinct().count()
            })
    
    # Sort by hours
    selected_range_work_hours.sort(key=lambda x: x['hours'], reverse=True)
    current_month_work_hours.sort(key=lambda x: x['hours'], reverse=True)
    prev_month_work_hours.sort(key=lambda x: x['hours'], reverse=True)
    
    # Active vacations in selected range
    active_vacations = Vacation.objects.filter(
        user__company=company,
        is_active=True,
        date_from__lte=date_to,
        date_to__gte=date_from
    ).count()
    
    # Calculate number of days in selected range
    days_in_range = (date_to - date_from).days + 1
    
    context = {
        'company': company,
        'today_arrivals': today_arrivals,
        'today_departures': today_departures,
        'week_scans': week_scans,
        'current_month_scans': current_month_scans,
        'prev_month_scans': prev_month_scans,
        'current_month_name': current_month_start.strftime('%B %Y'),
        'prev_month_name': prev_month_start.strftime('%B %Y'),
        'currently_in_office': currently_in_office,
        'currently_in_office_count': len(currently_in_office),
        'top_qr_codes': top_qr_codes,
        'selected_range_work_hours': selected_range_work_hours,
        'current_month_work_hours': current_month_work_hours,
        'prev_month_work_hours': prev_month_work_hours,
        'total_users': users.count(),
        'total_qr_codes': qr_codes.count(),
        'active_vacations': active_vacations,
        'date_from': date_from.strftime('%Y-%m-%d'),
        'date_to': date_to.strftime('%Y-%m-%d'),
        'date_range_display': f"{date_from.strftime('%d.%m.%Y')} - {date_to.strftime('%d.%m.%Y')}",
        'range_arrivals': range_arrivals,
        'range_departures': range_departures,
        'range_total_scans': range_total_scans,
        'days_in_range': days_in_range,
    }
    
    return render(request, 'company_analytics.html', context)


def analytics_chart_data(request):
    """API endpoint for chart data (JSON)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        return JsonResponse({'error': 'Company not found'}, status=404)
    
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    chart_type = request.GET.get('type', 'daily')
    days = int(request.GET.get('days', 7))
    
    today = timezone.now().date()
    start_date = today - timedelta(days=days-1)
    
    if chart_type == 'daily':
        # Daily scan counts
        data = []
        labels = []
        arrivals_data = []
        departures_data = []
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            labels.append(date.strftime('%d.%m'))
            
            day_scans = ScanEvent.objects.filter(
                qr_code__company=company,
                timestamp__date=date
            )
            
            arrivals = day_scans.filter(scan_type='arrival').count()
            departures = day_scans.filter(scan_type='departure').count()
            
            arrivals_data.append(arrivals)
            departures_data.append(departures)
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': str(_('Arrivals')),
                    'data': arrivals_data,
                    'borderColor': 'rgb(16, 185, 129)',
                    'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                    'tension': 0.4
                },
                {
                    'label': str(_('Departures')),
                    'data': departures_data,
                    'borderColor': 'rgb(239, 68, 68)',
                    'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                    'tension': 0.4
                }
            ]
        })
    
    elif chart_type == 'qr_usage':
        # QR code usage pie chart
        qr_data = ScanEvent.objects.filter(
            qr_code__company=company,
            timestamp__date__gte=start_date
        ).values('qr_code__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        labels = [item['qr_code__name'] for item in qr_data]
        data = [item['count'] for item in qr_data]
        
        colors = [
            'rgb(37, 99, 235)',
            'rgb(16, 185, 129)',
            'rgb(245, 158, 11)',
            'rgb(239, 68, 68)',
            'rgb(139, 92, 246)'
        ]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderWidth': 2,
                'borderColor': '#fff'
            }]
        })
    
    elif chart_type == 'hourly':
        # Hourly distribution (today)
        hours = list(range(24))
        labels = [f'{h:02d}:00' for h in hours]
        data = []
        
        for hour in hours:
            count = ScanEvent.objects.filter(
                qr_code__company=company,
                timestamp__date=today,
                timestamp__hour=hour
            ).count()
            data.append(count)
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': str(_('Scans')),
                'data': data,
                'backgroundColor': 'rgba(37, 99, 235, 0.5)',
                'borderColor': 'rgb(37, 99, 235)',
                'borderWidth': 2
            }]
        })
    
    return JsonResponse({'error': 'Invalid chart type'}, status=400)


# ============= MAGAZINE VIEWS =============

def magazine_dashboard(request):
    """Magazine dashboard - list all magazines for the company"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company to access this page'))
        return redirect('company_login')
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    magazines = Magazine.objects.filter(company_id=company_id).order_by('-modified_at')
    
    context = {
        'magazines': magazines,
        'company_id': company_id,
    }
    return render(request, 'magazine_dashboard.html', context)


def magazine_editor(request, magazine_id=None):
    """Magazine editor - create or edit a magazine"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company to access this page'))
        return redirect('company_login')
    
    from viewer.models import Magazine, MagazineArticle, User
    company_id = request.session['company_id']
    
    # Get or create magazine
    if magazine_id:
        magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
        if not magazine:
            messages.error(request, _('Magazine not found'))
            return redirect('magazine_dashboard')
    else:
        # Create new magazine
        user = User.objects.filter(company_id=company_id).first()
        magazine = Magazine.objects.create(
            company_id=company_id,
            created_by=user,
            title="New Magazine",
            issue_number="1",
            publish_date=datetime.date.today()
        )
        
        MagazineArticle.objects.create(
            magazine=magazine,
            author=user,
            title="Article 1",
            category="News"
        )
        
        return redirect('magazine_editor', magazine_id=magazine.id)
    
    # Get articles
    articles = magazine.articles.all()
    users = User.objects.filter(company_id=company_id, is_active=True)
    
    context = {
        'magazine': magazine,
        'articles': articles,
        'users': users,
        'categories': magazine.get_categories_list(),
    }
    return render(request, 'magazine_editor.html', context)


def magazine_preview(request, magazine_id):
    """Magazine preview - show print-ready preview"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, _('Please login as a company to access this page'))
        return redirect('company_login')
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        messages.error(request, _('Magazine not found'))
        return redirect('magazine_dashboard')
    
    articles = magazine.articles.all().order_by('order', 'page_number')
    
    context = {
        'magazine': magazine,
        'articles': articles,
    }
    return render(request, 'magazine_preview.html', context)


# ============= MAGAZINE API ENDPOINTS =============

@csrf_exempt
def api_magazine_update(request, magazine_id):
    """API: Update magazine configuration"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        return JsonResponse({'error': 'Magazine not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        
        # Update fields
        if 'title' in data:
            magazine.title = data['title']
        if 'issue_number' in data:
            magazine.issue_number = data['issue_number']
        if 'tagline' in data:
            magazine.tagline = data['tagline']
        if 'publish_date' in data:
            magazine.publish_date = data['publish_date']
        if 'template_id' in data:
            magazine.template_id = data['template_id']
        if 'primary_color' in data:
            magazine.primary_color = data['primary_color']
        if 'secondary_color' in data:
            magazine.secondary_color = data['secondary_color']
        if 'background_color' in data:
            magazine.background_color = data['background_color']
        if 'categories' in data:
            magazine.categories = data['categories']
        if 'cover_background_image' in data:
            magazine.cover_background_image = data['cover_background_image']
        if 'cover_header_position' in data:
            magazine.cover_header_position = data['cover_header_position']
        if 'primary_font' in data:
            magazine.primary_font = data['primary_font']
        if 'secondary_font' in data:
            magazine.secondary_font = data['secondary_font']
        if 'text_color' in data:
            magazine.text_color = data['text_color']
        
        magazine.save()
        
        return JsonResponse({'success': True, 'magazine': {
            'id': magazine.id,
            'title': magazine.title,
            'issue_number': magazine.issue_number,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_magazine_delete(request, magazine_id):
    """API: Delete a magazine"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import Magazine
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        return JsonResponse({'error': 'Magazine not found'}, status=404)
    
    magazine.delete()
    return JsonResponse({'success': True})


@csrf_exempt
def api_article_create(request, magazine_id):
    """API: Create a new article"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import Magazine, MagazineArticle, User
    company_id = request.session['company_id']
    
    magazine = Magazine.objects.filter(id=magazine_id, company_id=company_id).first()
    if not magazine:
        return JsonResponse({'error': 'Magazine not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        
        # Get author
        user = User.objects.filter(company_id=company_id).first()
        
        article = MagazineArticle.objects.create(
            magazine=magazine,
            author=user,
            title=data.get('title', 'New Article'),
            category=data.get('category', magazine.get_categories_list()[0]),
            status='draft'
        )
        
        return JsonResponse({'success': True, 'article': {
            'id': article.id,
            'title': article.title,
            'category': article.category,
            'status': article.status,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_article_update(request, article_id):
    """API: Update an article"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': 'Article not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        
        if 'title' in data:
            article.title = data['title']
        if 'teaser' in data:
            article.teaser = data['teaser']
        if 'category' in data:
            article.category = data['category']
        if 'status' in data:
            article.status = data['status']
        if 'is_main_story' in data:
            article.is_main_story = data['is_main_story']
        if 'is_secondary_story' in data:
            article.is_secondary_story = data['is_secondary_story']
        if 'order' in data:
            article.order = data['order']
        
        article.save()
        
        return JsonResponse({'success': True, 'article': {
            'id': article.id,
            'title': article.title,
            'status': article.status,
        }})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_article_delete(request, article_id):
    """API: Delete an article"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': 'Article not found'}, status=404)
    
    article.delete()
    return JsonResponse({'success': True})


@csrf_exempt
def api_content_block_create(request, article_id):
    """API: Create a content block"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import MagazineArticle, ContentBlock
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': 'Article not found'}, status=404)
    
    try:
        # Get next order
        max_order = article.content_blocks.aggregate(Max('order'))['order__max'] or 0
        
        # Check if it's a file upload (image)
        if request.FILES.get('image'):
            block = ContentBlock.objects.create(
                article=article,
                block_type='image',
                order=max_order + 1,
                image=request.FILES['image'],
                alignment='center'
            )
        else:
            # JSON data
            data = json.loads(request.body)
            
            block = ContentBlock.objects.create(
                article=article,
                block_type=data.get('block_type', 'text'),
                order=max_order + 1,
                text_content=data.get('text_content', ''),
                image_url=data.get('image_url', ''),
                alignment=data.get('alignment', 'left')
            )
        
        return JsonResponse({'success': True, 'block': {
            'id': block.id,
            'block_type': block.block_type,
            'order': block.order,
        }})
    except json.JSONDecodeError as e:
        return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=400)


@csrf_exempt
def api_content_block_update(request, block_id):
    """API: Update a content block"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import ContentBlock
    company_id = request.session['company_id']
    
    block = ContentBlock.objects.filter(
        id=block_id,
        article__magazine__company_id=company_id
    ).first()
    
    if not block:
        return JsonResponse({'error': 'Block not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        
        if 'text_content' in data:
            block.text_content = data['text_content']
        if 'image_url' in data:
            block.image_url = data['image_url']
        if 'image_caption' in data:
            block.image_caption = data['image_caption']
        if 'alignment' in data:
            block.alignment = data['alignment']
        if 'font_size' in data:
            block.font_size = data['font_size']
        if 'order' in data:
            block.order = data['order']
        
        block.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def api_content_block_delete(request, block_id):
    """API: Delete a content block"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import ContentBlock
    company_id = request.session['company_id']
    
    block = ContentBlock.objects.filter(
        id=block_id,
        article__magazine__company_id=company_id
    ).first()
    
    if not block:
        return JsonResponse({'error': 'Block not found'}, status=404)
    
    block.delete()
    return JsonResponse({'success': True})


@csrf_exempt
def api_article_reorder_blocks(request, article_id):
    """API: Reorder content blocks"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import MagazineArticle, ContentBlock
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': 'Article not found'}, status=404)
    
    try:
        data = json.loads(request.body)
        blocks = data.get('blocks', [])
        
        # Update each block's order
        for block_data in blocks:
            block = ContentBlock.objects.filter(
                id=block_data['id'],
                article=article
            ).first()
            if block:
                block.order = block_data['order']
                block.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def api_article_data(request, article_id):
    """API: Get article data with content blocks"""
    if 'company_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    from viewer.models import MagazineArticle
    company_id = request.session['company_id']
    
    article = MagazineArticle.objects.filter(
        id=article_id,
        magazine__company_id=company_id
    ).first()
    
    if not article:
        return JsonResponse({'error': 'Article not found'}, status=404)
    
    # Get content blocks
    blocks = []
    for block in article.content_blocks.all():
        block_data = {
            'id': block.id,
            'block_type': block.block_type,
            'order': block.order,
            'alignment': block.alignment,
        }
        
        if block.block_type == 'text':
            block_data['text_content'] = block.text_content
            block_data['font_size'] = block.font_size
        elif block.block_type == 'image':
            block_data['image_url'] = block.image_url
            block_data['image_caption'] = block.image_caption
            if block.image:
                block_data['image'] = block.image.url
        
        blocks.append(block_data)
    
    return JsonResponse({
        'success': True,
        'article': {
            'id': article.id,
            'title': article.title,
            'teaser': article.teaser,
            'category': article.category,
            'is_main_story': article.is_main_story,
            'is_secondary_story': article.is_secondary_story,
            'content_blocks': blocks
        }
    })