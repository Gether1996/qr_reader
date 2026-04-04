from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext_lazy as _, override
from django.conf import settings
from qr_reader_django import crud
import json
from viewer.models import ScanEvent, Vacation, PasswordResetToken, UserPasswordSetupToken
from viewer.account_texts import get_user_password_setup_texts, get_scan_mode_texts
from viewer.email_utils import get_email_language_code, render_localized_email, build_public_url
from qr_reader_django.audit import log_action, get_client_ip
from django.core.paginator import Paginator
from django.db.models import Q, F
import datetime

VALID_SCAN_TYPES = {'arrival', 'departure', 'lunch_break_start', 'lunch_break_end'}


def _get_page_size(request, default=20):
    raw_value = request.GET.get('per_page') or request.GET.get('items_per_page') or default
    try:
        value = int(raw_value)
        if value not in [10, 20, 25, 50, 100]:
            return default
        return value
    except (TypeError, ValueError):
        return default


def _get_enabled_scan_buttons(user):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    recent_scans = ScanEvent.objects.filter(
        scanned_by=user,
        timestamp__date__gte=yesterday
    ).order_by('timestamp')

    enabled_buttons = ['arrival']
    if recent_scans.exists():
        last_scan = recent_scans.last()
        if last_scan.scan_type == 'arrival':
            enabled_buttons = ['departure', 'lunch_break_start']
        elif last_scan.scan_type == 'lunch_break_start':
            enabled_buttons = ['lunch_break_end']
        elif last_scan.scan_type == 'lunch_break_end':
            enabled_buttons = ['departure', 'lunch_break_start']
        elif last_scan.scan_type == 'departure':
            enabled_buttons = ['arrival']

    return enabled_buttons

# ============= PUBLIC VIEWS =============

def download_android_apk(request):
    """Serve Android APK for direct download (sideloading without Google Play)."""
    import os
    from django.http import FileResponse, Http404
    apk_path = os.path.join(settings.BASE_DIR, 'static', 'apk', 'qr-reader.apk')
    if not os.path.exists(apk_path):
        raise Http404("APK not yet available.")
    response = FileResponse(open(apk_path, 'rb'), content_type='application/vnd.android.package-archive')
    response['Content-Disposition'] = 'attachment; filename="qr-reader.apk"'
    return response

def service_worker(request):
    """Serve PWA service worker at root scope (/sw.js).
    Must be outside i18n_patterns so it has global scope over the entire origin."""
    import os
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = '// Service Worker not found'
    response = HttpResponse(content, content_type='application/javascript; charset=utf-8')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def landing_page(request):
    """Landing page with links to company and user login"""
    # Redirect to dashboard if already logged in
    if 'company_id' in request.session and request.session.get('user_type') == 'company':
        return redirect('company_dashboard')
    elif 'user_id' in request.session and request.session.get('user_type') == 'user':
        return redirect('user_dashboard')
    
    return render(request, 'landing.html')


# ============= COMPANY AUTH VIEWS =============

def company_dashboard(request):
    """Company dashboard - manage QR codes, users, and absences"""
    # Allow both company owners and managers
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        messages.error(request, _('Please login as a company or manager'))
        return redirect('company_login')
    
    # Get company and current user
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
        current_user = None
    else:  # is_manager
        current_user = crud.get_user_by_id(request.session['user_id'])
        if not current_user or not current_user.is_manager:
            messages.error(request, _('Access denied'))
            return redirect('user_dashboard')
        company = current_user.company
    
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login' if is_company else 'user_login')
    
    # Determine permissions first
    can_edit_qr_codes = is_company or (current_user and current_user.can_edit_qr_codes)
    can_edit_employees = is_company or (current_user and current_user.can_edit_employees)
    can_edit_absences = is_company or (current_user and current_user.can_edit_absences)
    
    # Get active tab from query params
    requested_tab = request.GET.get('tab', '')
    
    # Validate tab permissions and set default if needed
    if requested_tab:
        # Check if user has permission for requested tab
        if requested_tab == 'qr-codes' and not can_edit_qr_codes:
            requested_tab = ''
        elif requested_tab == 'users' and not can_edit_employees:
            requested_tab = ''
        elif requested_tab == 'absences' and not can_edit_absences:
            requested_tab = ''
    
    # Set default tab if not specified or not permitted
    if not requested_tab:
        if can_edit_employees:
            active_tab = 'users'
        elif can_edit_absences:
            active_tab = 'absences'
        elif can_edit_qr_codes:
            active_tab = 'qr-codes'
        else:
            active_tab = 'users'  # fallback
    else:
        active_tab = requested_tab
    
    # Get filter parameters
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    vacation_type = request.GET.get('vacation_type', '')
    user_filter = request.GET.get('user', '')
    absence_employee_name = request.GET.get('absence_employee_name', '')
    qr_name = request.GET.get('qr_name', '')
    employee_name = request.GET.get('employee_name', '')
    work_status = request.GET.get('work_status', '')
    show_deactivated = request.GET.get('show_deactivated', '')
    items_per_page = request.GET.get('items_per_page', '25')
    sort = request.GET.get('sort', '')
    page_number = request.GET.get('page', 1)
    include_inactive_users = show_deactivated in ['1', 'true', 'on']
    
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
        if items_per_page not in [10, 20, 25, 50, 100]:
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
    
    # Active users remain the source for absence flows and employee pickers.
    active_users = crud.get_company_users(company)
    user_filter_datalist = crud.get_company_users(company, include_inactive=include_inactive_users)

    # Get users with filtering
    users = crud.get_company_users(company, include_inactive=include_inactive_users)
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
    
    # Calculate total scans for each user (including home office scans)
    # Store users as list to allow filtering by work status
    users_list = list(users)
    for user in users_list:
        # Include both regular QR scans and home office scans
        user.total_scans = ScanEvent.objects.filter(
            scanned_by=user
        ).filter(
            Q(qr_code__is_active=True) | Q(is_home_office=True) | Q(is_business_trip=True)
        ).count()
        
        # Get last scan to determine if user is at work (including home office)
        last_scan = ScanEvent.objects.filter(
            scanned_by=user
        ).filter(
            Q(qr_code__is_active=True) | Q(is_home_office=True) | Q(is_business_trip=True)
        ).order_by('-timestamp').first()
        
        if not user.is_active:
            user.is_at_work = False
            user.work_location = None
        elif last_scan:
            # User is at work if last scan was arrival or lunch_break_end
            user.is_at_work = last_scan.scan_type in ['arrival', 'lunch_break_end']
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
        user__is_active=True,
        is_active=True
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

    users_json = json.dumps([{'id': u.id, 'name': u.name} for u in active_users])

    context = {
        'company': company,
        'current_user': current_user,
        'is_company': is_company,
        'is_manager': is_manager,
        'can_edit_qr_codes': can_edit_qr_codes,
        'can_edit_employees': can_edit_employees,
        'can_edit_absences': can_edit_absences,
        'all_qr_codes': all_qr_codes,  # All QR codes for datalist
        'qr_codes': qr_codes_list if active_tab == 'qr-codes' else [],
        'users': active_users,
        'user_filter_datalist': user_filter_datalist,
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
            'show_deactivated': '1' if include_inactive_users else '',
            'items_per_page': str(items_per_page),
            'sort': sort,
        },
        'qr_codes_count': len(qr_codes_list),
        'users_count': len(users_list),
        'absences_count': absences.count(),
        'at_work_count': sum(1 for user in users_list if getattr(user, 'is_at_work', False)),
        'manager_count': sum(1 for user in users_list if getattr(user, 'is_manager', False)),
        'pending_absences_count': Vacation.objects.filter(
            user__company=company,
            user__is_active=True,
            is_active=True,
            approved=False,
        ).count(),
    }
    return render(request, 'company_dashboard.html', context)

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
    per_page = _get_page_size(request, default=20)
    
    # ===== SCANS TAB =====
    # Include both regular QR code scans and home office scans
    scans = ScanEvent.objects.filter(
        scanned_by=user
    ).filter(
        Q(qr_code__company=user.company, qr_code__is_active=True) | 
        Q(is_home_office=True, scanned_by__company=user.company) |
        Q(is_business_trip=True, scanned_by__company=user.company) |
        Q(is_no_qr=True, scanned_by__company=user.company)
    ).select_related('qr_code', 'scanned_by')
    
    # Scans-specific filters
    qr_code_filter = request.GET.get('qr_code', '')
    scan_type_filter = request.GET.get('scan_type', '')
    
    if qr_code_filter:
        # Filter by QR code name, but exclude home office scans (where qr_code is NULL)
        scans = scans.filter(qr_code__isnull=False, qr_code__name__icontains=qr_code_filter)
    
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
        # For QR code name sorting, handle NULL values (home office scans)
        if 'qr_code__name' in sort_by:
            # Sort with NULL values at the end
            if sort_by.startswith('-'):
                scans = scans.order_by(F('qr_code__name').desc(nulls_last=True))
            else:
                scans = scans.order_by(F('qr_code__name').asc(nulls_last=True))
        else:
            scans = scans.order_by(sort_by)
    else:
        scans = scans.order_by('-timestamp')
    
    # Pagination for scans
    scans_paginator = Paginator(scans, per_page)
    page_obj = scans_paginator.get_page(page_number)
    scans_count = scans.count()
    
    # ===== ABSENCES TAB =====
    absences = Vacation.objects.filter(user=user, is_active=True).order_by('-date_from')
    
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
    
    # Calculate year-to-date statistics
    from datetime import datetime
    current_year = datetime.now().year
    
    # Get approved absences for current year
    year_absences = Vacation.objects.filter(
        user=user,
        is_active=True,
        approved=True,
        date_from__year=current_year
    )
    
    vacation_days_ytd = sum(v.days_count for v in year_absences.filter(type='vacation'))
    sick_leave_days_ytd = sum(v.days_count for v in year_absences.filter(type='sick_leave'))
    doctor_days_ytd = sum(v.days_count for v in year_absences.filter(type='doctor'))
    remaining_vacation_days = max(user.holidays_per_year - vacation_days_ytd, 0)
    pending_absences_count = Vacation.objects.filter(user=user, is_active=True, approved=False).count()
    last_scan = scans.order_by('-timestamp').first()

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
        'vacation_days_ytd': vacation_days_ytd,
        'sick_leave_days_ytd': sick_leave_days_ytd,
        'doctor_days_ytd': doctor_days_ytd,
        'remaining_vacation_days': remaining_vacation_days,
        'pending_absences_count': pending_absences_count,
        'approved_absences_count': year_absences.count(),
        'last_scan': last_scan,
        'current_year': current_year,
        'current_filters': {
            'qr_code': qr_code_filter,
            'scan_type': scan_type_filter,
            'vacation_type': vacation_type_filter,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort_by,
            'per_page': per_page,
            'items_per_page': str(per_page),
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
            data = json.loads(request.body or '{}')
            scan_texts = get_scan_mode_texts(getattr(request, 'LANGUAGE_CODE', 'en'))
            uuid = (data.get('uuid') or '').strip()
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            scan_type = data.get('scan_type', 'arrival')
            is_home_office = data.get('is_home_office', False)
            is_business_trip = data.get('is_business_trip', False)
            is_no_qr = data.get('is_no_qr', False)

            if scan_type not in VALID_SCAN_TYPES:
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('Invalid scan type'))
                }, status=400)

            manual_mode_count = sum([
                bool(is_home_office),
                bool(is_business_trip),
                bool(is_no_qr),
            ])

            if manual_mode_count > 1:
                return JsonResponse({
                    'status': 'error',
                    'message': scan_texts['choose_one_mobile_mode']
                }, status=400)

            if latitude in (None, '') or longitude in (None, ''):
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('Location is required'))
                }, status=400)

            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (TypeError, ValueError):
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('Invalid location coordinates'))
                }, status=400)

            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('Location coordinates are out of range'))
                }, status=400)

            if not is_home_office and not is_business_trip and not is_no_qr and not uuid:
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('UUID is required'))
                }, status=400)

            enabled_buttons = _get_enabled_scan_buttons(user)
            if scan_type not in enabled_buttons:
                return JsonResponse({
                    'status': 'error',
                    'message': str(_('This scan type is not available right now'))
                }, status=409)
            
            # For mobile-only scan modes, we don't need a QR code
            if is_home_office or is_business_trip or is_no_qr:
                # Determine the label for this scan type
                if is_home_office:
                    scan_label = scan_texts['home_office']
                elif is_business_trip:
                    scan_label = scan_texts['business_trip']
                else:
                    scan_label = scan_texts['no_qr']
                
                # Record the scan without QR code
                scan, address = crud.create_scan_event(
                    qr_code=None,
                    scanned_by=user,
                    latitude=latitude,
                    longitude=longitude,
                    scan_type=scan_type,
                    device_info=request.META.get('HTTP_USER_AGENT', ''),
                    is_home_office=is_home_office,
                    is_business_trip=is_business_trip,
                    is_no_qr=is_no_qr,
                    actor_type='user',
                    actor_email=user.email,
                    actor_name=user.name,
                    ip_address=get_client_ip(request),
                    request=request
                )
                
                return JsonResponse({
                    'status': 'success',
                    'message': str(_('{} scan recorded successfully!').format(scan_label)),
                    'data': {
                        'qr_name': str(scan_label),
                        'qr_location': '',
                        'scan_timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'scan_latitude': latitude,
                        'scan_longitude': longitude,
                        'scan_address': address or str(_('Address not available'))
                    }
                })
            
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
            
            # Record the scan with audit logging
            scan, address = crud.create_scan_event(
                qr_code=qr_code,
                scanned_by=user,
                latitude=latitude,
                longitude=longitude,
                scan_type=scan_type,
                device_info=request.META.get('HTTP_USER_AGENT', ''),
                is_home_office=False,
                is_business_trip=False,
                is_no_qr=False,
                actor_type='user',
                actor_email=user.email,
                actor_name=user.name,
                ip_address=get_client_ip(request),
                request=request
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
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': str(_('Invalid request payload'))
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    enabled_buttons = _get_enabled_scan_buttons(user)
    
    context = {
        'user': user,
        'enabled_buttons': enabled_buttons,
    }
    return render(request, 'user_scan_qr.html', context)

def view_qr_scans(request, qr_id):
    """View all scans for a specific QR code with filtering and pagination"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')
    
    # Get company
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
    else:
        user = crud.get_user_by_id(request.session['user_id'])
        if not user or not user.is_manager or not user.can_edit_qr_codes:
            messages.error(request, _('Access denied'))
            return redirect('user_dashboard')
        company = user.company
    
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login' if is_company else 'user_login')
    
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
    per_page = _get_page_size(request, default=20)
    
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
            'items_per_page': str(per_page),
        }
    }
    return render(request, 'qr_scans.html', context)


def view_user_details(request, user_id):
    """View detailed information about a specific user with filtering and pagination"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        messages.error(request, _('Unauthorized'))
        return redirect('company_login')
    
    # Get company
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
        current_user = None
    else:
        current_user = crud.get_user_by_id(request.session['user_id'])
        if not current_user or not current_user.is_manager or not current_user.can_edit_employees:
            messages.error(request, _('Access denied'))
            return redirect('user_dashboard')
        company = current_user.company
    
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login' if is_company else 'user_login')
    
    user = crud.get_user_by_id(user_id, include_inactive=True)
    if not user or user.company != company:
        messages.error(request, _('User not found'))
        return redirect('company_dashboard')
    
    # Determine active tab
    active_tab = request.GET.get('tab', 'scans')
    
    # Filtering
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Pagination
    page_number = request.GET.get('page', 1)
    per_page = _get_page_size(request, default=20)
    
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
        vacations_count = Vacation.objects.filter(user=user, is_active=True).count()
        
        # Calculate year-to-date statistics
        from datetime import datetime as dt
        current_year = dt.now().year
        year_start = datetime.date(current_year, 1, 1)
        
        # Get approved absences for current year
        year_absences = Vacation.objects.filter(
            user=user,
            is_active=True,
            approved=True,
            date_from__year=current_year
        )
        
        vacation_days_ytd = sum(v.days_count for v in year_absences.filter(type='vacation'))
        sick_leave_days_ytd = sum(v.days_count for v in year_absences.filter(type='sick_leave'))
        doctor_days_ytd = sum(v.days_count for v in year_absences.filter(type='doctor'))
        
        context = {
            'company': company,
            'user': user,
            'vacations_page': vacations_page,
            'page_obj': vacations_page,  # For paginator template
            'has_active_filters': has_active_filters,
            'active_tab': active_tab,
            'scans_count': scans_count,
            'vacations_count': vacations_count,
            'is_company': is_company,
            'can_edit_absences': is_company or (current_user and current_user.can_edit_absences),
            'can_edit_employees': is_company or (current_user and current_user.can_edit_employees),
            'vacation_days_ytd': vacation_days_ytd,
            'sick_leave_days_ytd': sick_leave_days_ytd,
            'doctor_days_ytd': doctor_days_ytd,
            'current_year': current_year,
            'current_filters': {
                'date_from': date_from,
                'date_to': date_to,
                'vacation_type': vacation_type_filter,
                'sort': sort_by,
                'per_page': per_page,
                'items_per_page': str(per_page),
            }
        }
    else:
        # Get all scans by this user
        scans = ScanEvent.objects.filter(scanned_by=user).select_related('qr_code', 'scanned_by')
        
        # Additional filters for scans
        qr_code_filter = request.GET.get('qr_code', '')
        scan_type_filter = request.GET.get('scan_type', '')
        
        if qr_code_filter:
            # Filter by QR code name, but exclude home office scans (where qr_code is NULL)
            scans = scans.filter(qr_code__isnull=False, qr_code__name__icontains=qr_code_filter)
        
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
            # For QR code name sorting, handle NULL values (home office scans)
            if 'qr_code__name' in sort_by:
                # Sort with NULL values at the end
                if sort_by.startswith('-'):
                    scans = scans.order_by(F('qr_code__name').desc(nulls_last=True))
                else:
                    scans = scans.order_by(F('qr_code__name').asc(nulls_last=True))
            else:
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
        vacations_count = Vacation.objects.filter(user=user, is_active=True).count()
        
        # Calculate year-to-date statistics
        from datetime import datetime as dt
        current_year = dt.now().year
        year_start = datetime.date(current_year, 1, 1)
        
        # Get approved absences for current year
        year_absences = Vacation.objects.filter(
            user=user,
            is_active=True,
            approved=True,
            date_from__year=current_year
        )
        
        vacation_days_ytd = sum(v.days_count for v in year_absences.filter(type='vacation'))
        sick_leave_days_ytd = sum(v.days_count for v in year_absences.filter(type='sick_leave'))
        doctor_days_ytd = sum(v.days_count for v in year_absences.filter(type='doctor'))

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
            'is_company': is_company,
            'can_edit_absences': is_company or (current_user and current_user.can_edit_absences),
            'can_edit_employees': is_company or (current_user and current_user.can_edit_employees),
            'vacation_days_ytd': vacation_days_ytd,
            'sick_leave_days_ytd': sick_leave_days_ytd,
            'doctor_days_ytd': doctor_days_ytd,
            'current_year': current_year,
            'current_filters': {
                'qr_code': qr_code_filter,
                'scan_type': scan_type_filter,
                'date_from': date_from,
                'date_to': date_to,
                'sort': sort_by,
                'per_page': per_page,
                'items_per_page': str(per_page),
            }
        }
    return render(request, 'company_user_details.html', context)

def company_analytics(request):
    """Analytics dashboard with statistics and charts"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        messages.error(request, _('Please login as a company or manager'))
        return redirect('company_login')
    
    # Get company
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
    else:
        user = crud.get_user_by_id(request.session['user_id'])
        if not user or not user.is_manager:
            messages.error(request, _('Access denied'))
            return redirect('user_dashboard')
        company = user.company
    
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('company_login' if is_company else 'user_login')
    
    from django.db.models import Count, Q, Max
    from datetime import timedelta, datetime, date
    from calendar import monthrange
    
    today = date.today()
    
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
    
    # Today's statistics (always based on actual today) - include home office
    today_scans = ScanEvent.objects.filter(
        timestamp__date=today
    ).filter(
        Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
    )
    today_arrivals = today_scans.filter(scan_type='arrival').count()
    today_departures = today_scans.filter(scan_type='departure').count()
    
    # Statistics for selected date range - include home office
    range_scans = ScanEvent.objects.filter(
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    ).filter(
        Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
    )
    range_arrivals = range_scans.filter(scan_type='arrival').count()
    range_departures = range_scans.filter(scan_type='departure').count()
    range_total_scans = range_scans.count()
    
    # Weekly statistics
    week_scans = ScanEvent.objects.filter(
        timestamp__date__gte=week_ago
    ).filter(
        Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
    ).count()
    
    # Current month statistics
    current_month_scans = ScanEvent.objects.filter(
        timestamp__date__gte=current_month_start,
        timestamp__date__lte=today
    ).filter(
        Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
    ).count()
    
    # Previous month statistics
    prev_month_scans = ScanEvent.objects.filter(
        timestamp__date__gte=prev_month_start,
        timestamp__date__lte=prev_month_end
    ).filter(
        Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
    ).count()
    
    # Currently in office (last scan was arrival)
    currently_in_office = []
    for user in users:
        # Get last scan for this user (including home office scans)
        last_scan = ScanEvent.objects.filter(
            scanned_by=user
        ).filter(
            Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
        ).order_by('-timestamp').first()
        
        # User is at work if last scan was arrival or lunch_break_end
        if last_scan and last_scan.scan_type in ['arrival', 'lunch_break_end']:
            if last_scan.is_home_office:
                location = _('Home Office')
            elif last_scan.is_business_trip:
                location = _('Business Trip')
            elif last_scan.is_no_qr:
                location = _('No QR')
            else:
                location = last_scan.qr_code.name
            currently_in_office.append({
                'user': user,
                'location': location,
                'time': last_scan.timestamp
            })
    
    # Top 5 most used QR codes (for selected date range) - exclude home office scans
    top_qr_codes = ScanEvent.objects.filter(
        qr_code__company=company,
        qr_code__isnull=False,
        timestamp__date__gte=date_from,
        timestamp__date__lte=date_to
    ).values('qr_code__name', 'qr_code__location').annotate(
        scan_count=Count('id')
    ).order_by('-scan_count')[:5]
    
    # Calculate working hours for selected date range
    # Calculate number of days in selected period
    days_in_period = (date_to - date_from).days + 1
    # Calculate expected working hours based on days (assuming 30 days per month)
    avg_days_per_month = 30
    months_fraction = days_in_period / avg_days_per_month
    
    selected_range_work_hours = []
    for user in users:
        # Include both regular QR scans and home office scans
        scans = ScanEvent.objects.filter(
            scanned_by=user,
            timestamp__date__gte=date_from,
            timestamp__date__lte=date_to
        ).filter(
            Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
        ).order_by('timestamp')
        
        total_hours = 0
        arrival_time = None
        lunch_start_time = None
        
        for scan in scans:
            if scan.scan_type == 'arrival':
                arrival_time = scan.timestamp
            elif scan.scan_type == 'lunch_break_start' and arrival_time:
                lunch_start_time = scan.timestamp
            elif scan.scan_type == 'lunch_break_end' and lunch_start_time:
                lunch_start_time = None  # Reset lunch break
            elif scan.scan_type == 'departure' and arrival_time:
                departure_time = scan.timestamp
                work_duration = (departure_time - arrival_time).total_seconds() / 3600
                
                # Subtract lunch break duration if applicable
                if lunch_start_time:
                    lunch_duration = (departure_time - lunch_start_time).total_seconds() / 3600
                    work_duration -= lunch_duration
                
                total_hours += work_duration
                arrival_time = None
                lunch_start_time = None
        
        if total_hours > 0:  # Only include users with hours
            expected_hours = round(user.working_hours * months_fraction, 1)
            selected_range_work_hours.append({
                'user': user,
                'hours': round(total_hours, 1),
                'days': scans.values('timestamp__date').distinct().count(),
                'expected_hours': expected_hours
            })
    
    # Calculate working hours for current month (calendar)
    current_month_work_hours = []
    for user in users:
        # Include both regular QR scans and home office scans
        scans = ScanEvent.objects.filter(
            scanned_by=user,
            timestamp__date__gte=current_month_start,
            timestamp__date__lte=today
        ).filter(
            Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
        ).order_by('timestamp')
        
        total_hours = 0
        arrival_time = None
        lunch_start_time = None
        
        for scan in scans:
            if scan.scan_type == 'arrival':
                arrival_time = scan.timestamp
            elif scan.scan_type == 'lunch_break_start' and arrival_time:
                lunch_start_time = scan.timestamp
            elif scan.scan_type == 'lunch_break_end' and lunch_start_time:
                lunch_start_time = None  # Reset lunch break
            elif scan.scan_type == 'departure' and arrival_time:
                departure_time = scan.timestamp
                work_duration = (departure_time - arrival_time).total_seconds() / 3600
                
                # Subtract lunch break duration if applicable
                if lunch_start_time:
                    lunch_duration = (departure_time - lunch_start_time).total_seconds() / 3600
                    work_duration -= lunch_duration
                
                total_hours += work_duration
                arrival_time = None
                lunch_start_time = None
        
        if total_hours > 0:  # Only include users with hours
            current_month_work_hours.append({
                'user': user,
                'hours': round(total_hours, 1),
                'days': scans.values('timestamp__date').distinct().count()
            })
    
    # Calculate working hours for previous month
    prev_month_work_hours = []
    for user in users:
        # Include both regular QR scans and home office scans
        scans = ScanEvent.objects.filter(
            scanned_by=user,
            timestamp__date__gte=prev_month_start,
            timestamp__date__lte=prev_month_end
        ).filter(
            Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
        ).order_by('timestamp')
        
        total_hours = 0
        arrival_time = None
        lunch_start_time = None
        
        for scan in scans:
            if scan.scan_type == 'arrival':
                arrival_time = scan.timestamp
            elif scan.scan_type == 'lunch_break_start' and arrival_time:
                lunch_start_time = scan.timestamp
            elif scan.scan_type == 'lunch_break_end' and lunch_start_time:
                lunch_start_time = None  # Reset lunch break
            elif scan.scan_type == 'departure' and arrival_time:
                departure_time = scan.timestamp
                work_duration = (departure_time - arrival_time).total_seconds() / 3600
                
                # Subtract lunch break duration if applicable
                if lunch_start_time:
                    lunch_duration = (departure_time - lunch_start_time).total_seconds() / 3600
                    work_duration -= lunch_duration
                
                total_hours += work_duration
                arrival_time = None
                lunch_start_time = None
        
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
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_manager = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_manager):
        return JsonResponse({'error': str(_('Unauthorized'))}, status=401)
    
    # Get company
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
    else:
        user = crud.get_user_by_id(request.session['user_id'])
        if not user or not user.is_manager:
            return JsonResponse({'error': str(_('Access denied'))}, status=403)
        company = user.company
    
    if not company:
        return JsonResponse({'error': str(_('Company not found'))}, status=404)
    
    from django.db.models import Count
    from datetime import timedelta, date
    
    chart_type = request.GET.get('type', 'daily')
    days = int(request.GET.get('days', 7))
    
    today = date.today()
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
            
            # Include both regular QR scans and home office scans
            day_scans = ScanEvent.objects.filter(
                timestamp__date=date
            ).filter(
                Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
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
        # QR code usage pie chart - exclude home office scans (where qr_code is NULL)
        qr_data = ScanEvent.objects.filter(
            qr_code__company=company,
            qr_code__isnull=False,
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
            # Include both regular QR scans and home office scans
            count = ScanEvent.objects.filter(
                timestamp__date=today,
                timestamp__hour=hour
            ).filter(
                Q(qr_code__company=company) | Q(is_home_office=True, scanned_by__company=company) | Q(is_business_trip=True, scanned_by__company=company) | Q(is_no_qr=True, scanned_by__company=company)
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
    
    return JsonResponse({'error': str(_('Invalid chart type'))}, status=400)

def audit_logs(request):
    """View audit logs - company and managers see all, regular users see only their own"""
    is_company = request.session.get('user_type') == 'company' and 'company_id' in request.session
    is_user = request.session.get('user_type') == 'user' and 'user_id' in request.session
    
    if not (is_company or is_user):
        messages.error(request, _('Please login to access this page'))
        return redirect('landing_page')
    
    from viewer.models import AuditLog
    
    # Get company and current user
    if is_company:
        company = crud.get_company_by_id(request.session['company_id'])
        current_user = None
        is_manager = False
    else:
        current_user = crud.get_user_by_id(request.session['user_id'])
        if not current_user:
            messages.error(request, _('User not found'))
            return redirect('user_login')
        company = current_user.company
        is_manager = current_user.is_manager
    
    if not company:
        messages.error(request, _('Company not found'))
        return redirect('landing_page')
    
    # Get all logs - filter based on user type
    if is_company or is_manager:
        # Company and managers see all logs for their company
        # Get all user emails from company
        users = company.users.filter(is_active=True).values_list('email', flat=True)
        logs = AuditLog.objects.filter(
            Q(actor_email=company.email) | Q(actor_email__in=users)
        )
    else:
        # Regular users see only their own logs
        logs = AuditLog.objects.filter(actor_email=current_user.email)
    
    # Filtering
    actor_filter = request.GET.get('actor', '')
    action_filter = request.GET.get('action', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if actor_filter:
        logs = logs.filter(Q(actor_name__icontains=actor_filter) | Q(actor_email__icontains=actor_filter))
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if date_from and date_to:
        from datetime import datetime
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            logs = logs.filter(timestamp__date__gte=date_from_obj.date(), timestamp__date__lte=date_to_obj.date())
        except:
            messages.error(request, _('Invalid date range'))
    
    # Sorting
    sort = request.GET.get('sort', '-timestamp')
    valid_sort_fields = ['timestamp', '-timestamp', 'actor_name', '-actor_name', 'action', '-action']
    
    if sort in valid_sort_fields:
        logs = logs.order_by(sort)
    else:
        logs = logs.order_by('-timestamp')
    
    # Pagination
    items_per_page = request.GET.get('items_per_page', '25')
    try:
        items_per_page = int(items_per_page)
        if items_per_page not in [10, 25, 50, 100]:
            items_per_page = 25
    except (ValueError, TypeError):
        items_per_page = 25
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(logs, items_per_page)
    page_obj = paginator.get_page(page_number)
    
    # Get unique values for filters
    if is_company or is_manager:
        all_logs = AuditLog.objects.filter(
            Q(actor_email=company.email) | Q(actor_email__in=users)
        )
    else:
        all_logs = AuditLog.objects.filter(actor_email=current_user.email)
    
    # Get unique actors and actions, excluding empty values
    unique_actors = sorted(set(filter(None, all_logs.values_list('actor_name', flat=True).distinct())))
    unique_actions = sorted(set(filter(None, all_logs.values_list('action', flat=True).distinct())))
    
    context = {
        'company': company,
        'current_user': current_user,
        'is_company': is_company,
        'is_manager': is_manager,
        'page_obj': page_obj,
        'logs_count': logs.count(),
        'unique_actors': unique_actors,
        'unique_actions': unique_actions,
        'current_filters': {
            'actor': actor_filter,
            'action': action_filter,
            'date_from': date_from,
            'date_to': date_to,
            'sort': sort,
            'items_per_page': str(items_per_page),
        }
    }
    return render(request, 'audit_logs.html', context)

def company_settings(request):
    """Company settings page - view and edit company profile"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return redirect('company_login')
    
    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        return redirect('company_login')
    
    if request.method == 'POST':
        # Handle Ajax request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                company_name = request.POST.get('company_name', '').strip()
                auto_lunch_breaks = request.POST.get('auto_lunch_breaks') == 'True'
                
                # Notification preferences
                notify_arrival = request.POST.get('notify_arrival') == 'on'
                notify_departure = request.POST.get('notify_departure') == 'on'
                notify_vacation = request.POST.get('notify_vacation') == 'on'
                
                # Optional company details
                ico = request.POST.get('ico', '').strip() or None
                dic = request.POST.get('dic', '').strip() or None
                phone = request.POST.get('phone', '').strip() or None
                street = request.POST.get('street', '').strip() or None
                street_number = request.POST.get('street_number', '').strip() or None
                zip_code = request.POST.get('zip_code', '').strip() or None
                city = request.POST.get('city', '').strip() or None
                state = request.POST.get('state', '').strip() or None
                
                # Validation
                if not company_name:
                    return JsonResponse({
                        'success': False,
                        'message': str(_('Company name is required'))
                    })
                
                # Update company
                company.name = company_name
                company.auto_lunch_breaks = auto_lunch_breaks
                company.notify_arrival = notify_arrival
                company.notify_departure = notify_departure
                company.notify_vacation = notify_vacation
                company.ico = ico
                company.dic = dic
                company.phone = phone
                company.street = street
                company.street_number = street_number
                company.zip_code = zip_code
                company.city = city
                company.state = state
                company.save()
                
                # Log the action
                log_action(
                    actor_type='company',
                    actor_email=company.email,
                    actor_name=company.name,
                    action='update',
                    message=f'Company "{company.name}" updated profile settings',
                    ip_address=get_client_ip(request)
                )
                
                return JsonResponse({
                    'success': True,
                    'message': str(_('Settings saved successfully'))
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': str(_('An error occurred while saving settings'))
                })
        
    return render(request, 'company_settings.html', {
        'company': company
    })


def company_request_password_reset(request):
    """Handle password reset request - generate token and send email"""
    # Accept both regular POST and Ajax POST
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'success': False, 'message': str(_('Unauthorized'))})
    
    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        return JsonResponse({'success': False, 'message': str(_('Company not found'))})
    
    try:
        import secrets
        from datetime import timedelta, datetime
        from django.core.mail import send_mail
        
        # Invalidate any existing tokens
        PasswordResetToken.objects.filter(company=company, is_used=False).update(is_used=True)
        
        # Generate new token
        token = secrets.token_urlsafe(48)
        expires_at = datetime.now() + timedelta(hours=24)
        
        # Create token record
        reset_token = PasswordResetToken.objects.create(
            company=company,
            token=token,
            expires_at=expires_at
        )
        
        language_code = get_email_language_code(request=request)

        reset_url = build_public_url(request=request, path=f'/{language_code}/company/reset-password/{token}/')

        # Render email template
        email_html, language_code = render_localized_email('password_reset_email.html', {
            'company_name': company.name,
            'company_email': company.email,
            'reset_url': reset_url,
            'request_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }, language_code=language_code, request=request)

        with override(language_code):
            subject = str(_('Password Reset Request'))

        # Send email
        send_mail(
            subject=subject,
            message=f'Reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[company.email],
            html_message=email_html,
            fail_silently=False
        )
        
        # Log the action
        log_action(
            actor_type='company',
            actor_email=company.email,
            actor_name=company.name,
            action='request_password_reset',
            message=f'Company "{company.name}" requested password reset',
            ip_address=get_client_ip(request)
        )
        
        return JsonResponse({
            'success': True,
            'message': str(_('Password reset link has been sent to your email'))
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(_('Failed to send password reset email'))
        })


def company_reset_password(request, token):
    """Handle password reset with token"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        # Validate token
        if not reset_token.is_valid():
            messages.error(request, _('This password reset link has expired or is invalid'))
            return redirect('company_login')
        
        company = reset_token.company
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            
            # Validation
            if not new_password or not confirm_password:
                messages.error(request, _('Both password fields are required'))
                return render(request, 'company_reset_password.html', {
                    'token': token,
                    'company': company
                })
            
            if new_password != confirm_password:
                messages.error(request, _('Passwords do not match'))
                return render(request, 'company_reset_password.html', {
                    'token': token,
                    'company': company
                })
            
            if len(new_password) < 6:
                messages.error(request, _('Password must be at least 6 characters long'))
                return render(request, 'company_reset_password.html', {
                    'token': token,
                    'company': company
                })
            
            # Update password
            company.set_password(new_password)
            company.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Log the action
            log_action(
                actor_type='company',
                actor_email=company.email,
                actor_name=company.name,
                action='reset_password',
                message=f'Company "{company.name}" reset password',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, _('Password has been reset successfully. Please login with your new password.'))
            return redirect('company_login')
        
        return render(request, 'company_reset_password.html', {
            'token': token,
            'company': company
        })
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, _('Invalid password reset link'))
        return redirect('company_login')


def user_set_password(request, token):
    """Allow a newly invited employee to set their password"""
    copy = get_user_password_setup_texts(getattr(request, 'LANGUAGE_CODE', 'en'))

    try:
        setup_token = UserPasswordSetupToken.objects.select_related('user__company').get(token=token)
    except UserPasswordSetupToken.DoesNotExist:
        messages.error(request, copy['invalid_link'])
        return redirect('user_login')

    if not setup_token.is_valid():
        messages.error(request, copy['invalid_link'])
        return redirect('user_login')

    user = setup_token.user
    company = user.company

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            messages.error(request, copy['required_fields'])
        elif new_password != confirm_password:
            messages.error(request, copy['passwords_mismatch'])
        elif len(new_password) < 10:
            messages.error(request, copy['password_length_error'])
        elif not any(char.isupper() for char in new_password):
            messages.error(request, copy['password_uppercase_error'])
        else:
            user.set_password(new_password)
            user.save(update_fields=['password'])

            setup_token.is_used = True
            setup_token.save(update_fields=['is_used'])
            UserPasswordSetupToken.objects.filter(user=user, is_used=False).exclude(pk=setup_token.pk).update(is_used=True)

            log_action(
                actor_type='user',
                actor_email=user.email,
                actor_name=user.name,
                action='update',
                message=f'User "{user.name}" completed account password setup',
                ip_address=get_client_ip(request)
            )

            messages.success(request, copy['success_message'])
            return redirect('user_login')

    return render(request, 'user_password_setup.html', {
        'token': token,
        'user': user,
        'company': company,
        'copy': copy,
    })
