from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from qr_reader_django import crud
import json

# ============= PUBLIC VIEWS =============

def landing_page(request):
    """Landing page with links to company and user login"""
    return render(request, 'landing.html')


def scan_qr(request, uuid):
    """Public page for scanning QR codes - logs location and timestamp"""
    qr_code = crud.get_qr_code_by_uuid(uuid)
    if not qr_code:
        messages.error(request, 'QR code not found or inactive')
        return redirect('landing_page')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            device_info = data.get('device_info', '')

            # Get user if logged in
            user = None
            if 'user_id' in request.session:
                user = crud.get_user_by_id(request.session['user_id'])

            scan, address = crud.create_scan_event(
                qr_code=qr_code,
                latitude=latitude,
                longitude=longitude,
                scanned_by=user,
                device_info=device_info
            )
            
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

        company, error = crud.create_company(name, email, password)
        if error:
            messages.error(request, error)
            return render(request, 'company_register.html')

        messages.success(request, 'Company registered successfully! Please login.')
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

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, 'Company not found')
        return redirect('company_login')
    
    qr_codes = crud.get_company_qr_codes(company)
    users = crud.get_company_users(company)
    recent_scans = crud.get_company_scans(company, limit=20)

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

        user = crud.get_user_by_email(email)
        if user and user.check_password(password):
            request.session['user_id'] = user.id
            request.session['user_type'] = 'user'
            messages.success(request, f'Welcome back, {user.name}!')
            return redirect('user_dashboard')
        else:
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

    user = crud.get_user_by_id(request.session['user_id'])
    if not user:
        messages.error(request, 'User not found')
        return redirect('user_login')
    
    qr_codes = user.company.qr_codes.filter(is_active=True).order_by('-created_at')
    recent_scans = crud.get_company_scans(user.company, limit=20)

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

    user = crud.get_user_by_id(request.session['user_id'])
    if not user:
        messages.error(request, 'User not found')
        return redirect('user_login')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uuid = data.get('uuid')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            # Check if QR code exists and belongs to user's company
            qr_code = crud.get_qr_code_by_uuid(uuid)
            
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
            scan, address = crud.create_scan_event(
                qr_code=qr_code,
                scanned_by=user,
                latitude=latitude,
                longitude=longitude,
                device_info=request.META.get('HTTP_USER_AGENT', '')
            )
            
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
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': 'Company not found'}, status=404)
            
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

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, 'Company not found')
        return redirect('company_login')
    
    success, error = crud.deactivate_qr_code(qr_id, company)
    if success:
        messages.success(request, 'QR code deactivated successfully')
    else:
        messages.error(request, error or 'Failed to deactivate QR code')
    
    return redirect('company_dashboard')


def create_user(request):
    """Register a new user under the company (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': 'Company not found'}, status=404)
            
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
                'message': 'User created successfully',
                'user_id': user.id
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def edit_user(request, user_id):
    """Edit user details (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': 'Company not found'}, status=404)
            
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
                'message': 'User updated successfully'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def delete_user(request, user_id):
    """Delete user (company only)"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            company = crud.get_company_by_id(request.session['company_id'])
            if not company:
                return JsonResponse({'status': 'error', 'message': 'Company not found'}, status=404)
            
            success, error = crud.delete_user(user_id, company)
            
            if success:
                return JsonResponse({
                    'status': 'success',
                    'message': 'User deleted successfully'
                })
            else:
                return JsonResponse({'status': 'error', 'message': error}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def view_qr_scans(request, qr_id):
    """View all scans for a specific QR code"""
    if 'company_id' not in request.session or request.session.get('user_type') != 'company':
        messages.error(request, 'Unauthorized')
        return redirect('company_login')

    company = crud.get_company_by_id(request.session['company_id'])
    if not company:
        messages.error(request, 'Company not found')
        return redirect('company_login')
    
    qr_code = crud.get_qr_code_by_id(qr_id, company)
    if not qr_code:
        messages.error(request, 'QR code not found')
        return redirect('company_dashboard')
    
    scans = crud.get_qr_code_scans(qr_code)

    context = {
        'company': company,
        'qr_code': qr_code,
        'scans': scans,
    }
    return render(request, 'qr_scans.html', context)