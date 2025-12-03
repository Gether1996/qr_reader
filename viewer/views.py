from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
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
    qr_code_names = [qr.name for qr in qr_codes]
    
    # Check if any filters are active
    has_active_filters = any([qr_code_filter, scan_type_filter, date_from, date_to])

    context = {
        'user': user,
        'page_obj': page_obj,
        'qr_codes': qr_codes,
        'has_active_filters': has_active_filters,
        'datalist_items': qr_code_names,
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
    
    # Get all QR codes for datalist
    qr_codes = crud.get_company_qr_codes(company)
    qr_code_names = [qr.name for qr in qr_codes]

    context = {
        'company': company,
        'user': user,
        'page_obj': page_obj,
        'has_active_filters': has_active_filters,
        'datalist_items': qr_code_names,
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


def generate_attendance_pdf(request, user_id):
    """Generate PDF attendance report for a user"""
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime, timedelta
    from collections import defaultdict
    from io import BytesIO
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
    
    # Calculate statistics
    total_days = len(daily_data)
    total_work_hours = 0
    days_with_issues = []
    
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
    
    # Use Django's date formatting for proper localization
    from django.utils.formats import date_format
    
    current_date = date_from.date()
    while current_date <= date_to.date():
        day_scans = daily_data.get(current_date, [])
        # Use Django's date_format with 'l' format (day of the week)
        day_name = date_format(current_date, format='l')
        
        if not day_scans:
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
            # Find arrivals and departures
            arrivals = [s for s in day_scans if s.scan_type == 'arrival']
            departures = [s for s in day_scans if s.scan_type == 'departure']
            
            # Check for issues
            notes = []
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
            
            table_data.append([
                Paragraph(current_date.strftime('%d.%m.%Y'), cell_style_centered),
                Paragraph(day_name, cell_style),
                Paragraph(arrival_time, cell_style_centered),
                Paragraph(departure_time, cell_style_centered),
                Paragraph(hours_str, cell_style_centered),
                Paragraph(qr_info, cell_style),
                Paragraph(' '.join(notes) if notes else '✓', cell_style)
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
    
    # Summary statistics
    elements.append(Paragraph(str(_('Summary Statistics')), heading_style))
    
    avg_hours = total_work_hours / total_days if total_days > 0 else 0
    
    # Create styled summary data
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
    
    elements.append(summary_table)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response - serve from file
    with open(filepath, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    return response