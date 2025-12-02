from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from viewer.models import Company, User, QRCodeProfile, ScanEvent
import json
from datetime import datetime


# ============= PUBLIC VIEWS =============

def landing_page(request):
    """Landing page with links to company and user login"""
    return render(request, 'landing.html')


def scan_qr(request, uuid):
    """Public page for scanning QR codes - logs location and timestamp"""
    qr_code = get_object_or_404(QRCodeProfile, uuid=uuid, is_active=True)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            device_info = data.get('device_info', '')

            # Get user if logged in
            user = None
            if 'user_id' in request.session:
                user = User.objects.filter(id=request.session['user_id']).first()

            scan = ScanEvent.objects.create(
                qr_code=qr_code,
                scanned_by=user,
                latitude=latitude,
                longitude=longitude,
                device_info=device_info
            )
            
            # Get address from coordinates
            address = scan.get_address_from_coordinates()
            if address:
                scan.address = address
                scan.save()
            
            return JsonResponse({'status': 'success', 'message': 'Scan recorded successfully!'})
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
            messages.error(request, 'All fields are required')
            return render(request, 'company_register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'company_register.html')

        if Company.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'company_register.html')

        company = Company.objects.create(name=name, email=email)
        company.set_password(password)
        company.save()

        messages.success(request, 'Company registered successfully! Please login.')
        return redirect('company_login')

    return render(request, 'company_register.html')


def company_login(request):
    """Company login page"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            company = Company.objects.get(email=email, is_active=True)
            if company.check_password(password):
                request.session['company_id'] = company.id
                request.session['user_type'] = 'company'
                messages.success(request, f'Welcome back, {company.name}!')
                return redirect('company_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except Company.DoesNotExist:
            messages.error(request, 'Invalid credentials')

    return render(request, 'company_login.html')


def company_logout(request):
    """Company logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('landing_page')


def company_dashboard(request):
    """Company dashboard - manage QR codes and users"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, 'Please login as a company')
        return redirect('company_login')

    company = get_object_or_404(Company, id=request.session['company_id'])
    qr_codes = company.qr_codes.all().order_by('-created_at')
    users = company.users.all().order_by('-created_at')
    
    # Get recent scans
    recent_scans = ScanEvent.objects.filter(
        qr_code__company=company
    ).order_by('-timestamp')[:20]

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

        try:
            user = User.objects.get(email=email, is_active=True)
            if user.check_password(password):
                request.session['user_id'] = user.id
                request.session['user_type'] = 'user'
                messages.success(request, f'Welcome back, {user.name}!')
                return redirect('user_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except User.DoesNotExist:
            messages.error(request, 'Invalid credentials')

    return render(request, 'user_login.html')


def user_logout(request):
    """User logout"""
    request.session.flush()
    messages.success(request, 'Logged out successfully')
    return redirect('landing_page')


def user_dashboard(request):
    """User dashboard - view company QR codes and scans"""
    if 'user_id' not in request.session or request.session.get('user_type') != 'user':
        messages.error(request, 'Please login as a user')
        return redirect('user_login')

    user = get_object_or_404(User, id=request.session['user_id'])
    qr_codes = user.company.qr_codes.filter(is_active=True).order_by('-created_at')
    
    # Get scans for this user's company
    recent_scans = ScanEvent.objects.filter(
        qr_code__company=user.company
    ).order_by('-timestamp')[:20]

    context = {
        'user': user,
        'qr_codes': qr_codes,
        'recent_scans': recent_scans,
    }
    return render(request, 'user_dashboard.html', context)


def user_scan_qr(request):
    """User QR scanner page"""
    if 'user_id' not in request.session or request.session.get('user_type') != 'user':
        messages.error(request, 'Please login as a user')
        return redirect('user_login')

    user = get_object_or_404(User, id=request.session['user_id'])
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uuid = data.get('uuid')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            # Check if QR code exists and belongs to user's company
            qr_code = QRCodeProfile.objects.filter(uuid=uuid, is_active=True).first()
            
            if not qr_code:
                return JsonResponse({
                    'status': 'error',
                    'message': 'QR code not found or inactive'
                }, status=404)
            
            if qr_code.company != user.company:
                return JsonResponse({
                    'status': 'error',
                    'message': 'This QR code does not belong to your company'
                }, status=403)
            
            # Record the scan
            scan = ScanEvent.objects.create(
                qr_code=qr_code,
                scanned_by=user,
                latitude=latitude,
                longitude=longitude,
                device_info=request.META.get('HTTP_USER_AGENT', '')
            )
            
            # Get address from coordinates
            address = scan.get_address_from_coordinates()
            if address:
                scan.address = address
                scan.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Scan recorded successfully!',
                'data': {
                    'qr_name': qr_code.name,
                    'qr_location': qr_code.location,
                    'scan_timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'scan_latitude': latitude,
                    'scan_longitude': longitude,
                    'scan_address': address or 'Address not available'
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
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = Company.objects.get(id=request.session['company_id'])
            
            qr_code = QRCodeProfile.objects.create(
                company=company,
                name=data.get('name'),
                location=data.get('location'),
                additional_info=data.get('additional_info', '')
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'QR code created successfully',
                'qr_code_id': qr_code.id,
                'uuid': qr_code.uuid
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def delete_qr_code(request, qr_id):
    """Delete/deactivate a QR code (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, 'Unauthorized')
        return redirect('company_login')

    company = get_object_or_404(Company, id=request.session['company_id'])
    qr_code = get_object_or_404(QRCodeProfile, id=qr_id, company=company)
    qr_code.is_active = False
    qr_code.save()
    
    messages.success(request, 'QR code deactivated successfully')
    return redirect('company_dashboard')


def create_user(request):
    """Register a new user under the company (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = Company.objects.get(id=request.session['company_id'])
            
            email = data.get('email')
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already exists'}, status=400)
            
            user = User.objects.create(
                company=company,
                name=data.get('name'),
                email=email
            )
            user.set_password(data.get('password'))
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'User created successfully',
                'user_id': user.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def view_qr_scans(request, qr_id):
    """View all scans for a specific QR code"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, 'Unauthorized')
        return redirect('company_login')

    company = get_object_or_404(Company, id=request.session['company_id'])
    qr_code = get_object_or_404(QRCodeProfile, id=qr_id, company=company)
    scans = qr_code.scans.all().order_by('-timestamp')

    context = {
        'company': company,
        'qr_code': qr_code,
        'scans': scans,
    }
    return render(request, 'qr_scans.html', context)