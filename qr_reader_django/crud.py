from django.utils.translation import gettext_lazy as _, get_language, activate
from viewer.models import Company, User, QRCodeProfile, ScanEvent, Vacation
from datetime import datetime
from qr_reader_django.audit import log_action
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import sys
import secrets

# ============= COMPANY CRUD =============

def create_company(name, email, password, auto_lunch_breaks=False, notify_arrival=False, notify_departure=False, notify_vacation=False, ico=None, dic=None, phone=None, street=None, street_number=None, zip_code=None, city=None, state=None, ip_address=None):
    """Create a new company"""
    if Company.objects.filter(email=email).exists():
        return None, str(_('Email already registered'))
    
    company = Company.objects.create(
        name=name, 
        email=email, 
        auto_lunch_breaks=auto_lunch_breaks,
        notify_arrival=notify_arrival,
        notify_departure=notify_departure,
        notify_vacation=notify_vacation,
        ico=ico,
        dic=dic,
        phone=phone,
        street=street,
        street_number=street_number,
        zip_code=zip_code,
        city=city,
        state=state
    )
    company.set_password(password)
    company.save()
    
    log_action(
        actor_type='company',
        actor_email=email,
        actor_name=name,
        action='create',
        message=f'Company "{name}" registered',
        ip_address=ip_address
    )
    
    return company, None


def get_company_by_email(email):
    """Get company by email"""
    try:
        return Company.objects.get(email=email, is_active=True)
    except Company.DoesNotExist:
        return None


def get_company_by_id(company_id):
    """Get company by ID"""
    try:
        return Company.objects.get(id=company_id, is_active=True)
    except Company.DoesNotExist:
        return None


# ============= USER CRUD =============

def create_user(company, name, email, password, basic_work_hours=160, holidays_per_year=20, has_lunch_break=True, lunch_break_duration=30, is_manager=False, can_edit_employees=False, can_edit_qr_codes=False, can_edit_absences=False, notify_arrival=False, notify_departure=False, notify_vacation=False, rc=None, phone=None, birth_date=None, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Create a new user under a company"""
    if User.objects.filter(email=email).exists():
        return None, str(_('Email already exists'))

    raw_password = password or secrets.token_urlsafe(24)

    notifications_enabled = is_manager and any([notify_arrival, notify_departure, notify_vacation])
    
    user = User.objects.create(
        company=company,
        name=name,
        email=email,
        rc=rc,
        phone=phone,
        birth_date=birth_date,
        working_hours=basic_work_hours,
        holidays_per_year=holidays_per_year,
        has_lunch_break=has_lunch_break,
        lunch_break_duration=lunch_break_duration,
        is_manager=is_manager,
        can_edit_employees=can_edit_employees if is_manager else False,
        can_edit_qr_codes=can_edit_qr_codes if is_manager else False,
        can_edit_absences=can_edit_absences if is_manager else False,
        notifications=notifications_enabled,
        notify_arrival=notify_arrival if is_manager else False,
        notify_departure=notify_departure if is_manager else False,
        notify_vacation=notify_vacation if is_manager else False
    )
    user.set_password(raw_password)
    user.save()
    
    if actor_type and actor_email and actor_name:
        log_action(
            actor_type=actor_type,
            actor_email=actor_email,
            actor_name=actor_name,
            action='create',
            message=f'User "{name}" ({email}) created in company "{company.name}"',
            ip_address=ip_address
        )
    
    return user, None


def get_user_by_email(email):
    """Get user by email"""
    try:
        return User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return None


def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        return User.objects.get(id=user_id, is_active=True)
    except User.DoesNotExist:
        return None


def update_user(user_id, company, name=None, email=None, password=None, basic_work_hours=None, holidays_per_year=None, has_lunch_break=None, lunch_break_duration=None, is_active=None, is_manager=None, can_edit_employees=None, can_edit_qr_codes=None, can_edit_absences=None, notify_arrival=None, notify_departure=None, notify_vacation=None, rc=None, phone=None, birth_date=None, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Update user details"""
    try:
        user = User.objects.get(id=user_id, company=company)
        original_email = user.email
        
        # Check if email is being changed and if it already exists
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                return None, str(_('Email already exists'))
            user.email = email
        
        # Update name if provided
        if name:
            user.name = name
        
        # Update optional fields if provided
        if rc is not None:
            user.rc = rc
        if phone is not None:
            user.phone = phone
        if birth_date is not None:
            user.birth_date = birth_date
        
        # Update basic work hours if provided
        if basic_work_hours is not None:
            user.working_hours = basic_work_hours
        
        # Update holidays per year if provided
        if holidays_per_year is not None:
            user.holidays_per_year = holidays_per_year
        
        # Update has lunch break if provided
        if has_lunch_break is not None:
            user.has_lunch_break = has_lunch_break
        
        # Update lunch break duration if provided
        if lunch_break_duration is not None:
            user.lunch_break_duration = lunch_break_duration
        
        # Update manager status if provided
        if is_manager is not None:
            user.is_manager = is_manager
            # If changing from manager to employee, remove all permissions and notifications
            if not is_manager:
                user.can_edit_employees = False
                user.can_edit_qr_codes = False
                user.can_edit_absences = False
                user.notifications = False
                user.notify_arrival = False
                user.notify_departure = False
                user.notify_vacation = False
        
        # Update permissions if provided (only if user is manager)
        if user.is_manager:
            if can_edit_employees is not None:
                user.can_edit_employees = can_edit_employees
            if can_edit_qr_codes is not None:
                user.can_edit_qr_codes = can_edit_qr_codes
            if can_edit_absences is not None:
                user.can_edit_absences = can_edit_absences
            if notify_arrival is not None:
                user.notify_arrival = notify_arrival
            if notify_departure is not None:
                user.notify_departure = notify_departure
            if notify_vacation is not None:
                user.notify_vacation = notify_vacation
            user.notifications = any([
                user.notify_arrival,
                user.notify_departure,
                user.notify_vacation,
            ])
        else:
            user.notifications = False
        
        # Update status if provided
        if is_active is not None:
            user.is_active = is_active
        
        # Update password if provided
        if password:
            user.set_password(password)
        
        user.save()
        
        if actor_type and actor_email and actor_name:
            changes = []
            if name: changes.append(f'name to "{name}"')
            if email and email != original_email: changes.append(f'email to "{email}"')
            if basic_work_hours is not None: changes.append(f'working hours to {basic_work_hours}')
            if is_manager is not None: changes.append(f'manager status to {is_manager}')
            if password: changes.append('password')
            
            log_action(
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                action='update',
                message=f'User "{user.name}" updated: {", ".join(changes) if changes else "no changes"}',
                ip_address=ip_address
            )
        
        return user, None
    except User.DoesNotExist:
        return None, str(_('User not found'))


def delete_user(user_id, company, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Deactivate a user (soft delete)"""
    try:
        user = User.objects.get(id=user_id, company=company)
        user_name = user.name
        user_email = user.email
        user.is_active = False
        user.save()
        
        if actor_type and actor_email and actor_name:
            log_action(
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                action='delete',
                message=f'User "{user_name}" ({user_email}) deactivated',
                ip_address=ip_address
            )
        
        return True, None
    except User.DoesNotExist:
        return False, str(_('User not found'))


# ============= QR CODE CRUD =============

def create_qr_code(company, name, location, additional_info='', actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Create a new QR code"""
    qr_code = QRCodeProfile.objects.create(
        company=company,
        name=name,
        location=location,
        additional_info=additional_info
    )
    
    if actor_type and actor_email and actor_name:
        log_action(
            actor_type=actor_type,
            actor_email=actor_email,
            actor_name=actor_name,
            action='create',
            message=f'QR Code "{name}" created at location "{location}"',
            ip_address=ip_address
        )
    
    return qr_code, None


def get_qr_code_by_uuid(uuid):
    """Get QR code by UUID"""
    try:
        return QRCodeProfile.objects.get(uuid=uuid, is_active=True)
    except QRCodeProfile.DoesNotExist:
        return None


def get_qr_code_by_id(qr_id, company=None):
    """Get QR code by ID, optionally filtered by company"""
    try:
        if company:
            return QRCodeProfile.objects.get(id=qr_id, company=company)
        return QRCodeProfile.objects.get(id=qr_id)
    except QRCodeProfile.DoesNotExist:
        return None


def deactivate_qr_code(qr_id, company, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Deactivate a QR code"""
    try:
        qr_code = QRCodeProfile.objects.get(id=qr_id, company=company)
        qr_name = qr_code.name
        qr_code.is_active = False
        qr_code.save()
        
        if actor_type and actor_email and actor_name:
            log_action(
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                action='delete',
                message=f'QR Code "{qr_name}" deactivated',
                ip_address=ip_address
            )
        
        return True, None
    except QRCodeProfile.DoesNotExist:
        return False, str(_('QR code not found'))


def get_company_qr_codes(company):
    """Get all active QR codes for a company"""
    return company.qr_codes.filter(is_active=True).order_by('-created_at')


def get_company_users(company):
    """Get all active users for a company"""
    return company.users.filter(is_active=True).order_by('-created_at')


def get_company_scans(company, limit=20):
    """Get recent scans for a company (from active QR codes only)"""
    return ScanEvent.objects.filter(
        qr_code__company=company,
        qr_code__is_active=True
    ).order_by('-timestamp')[:limit]


def get_qr_code_scans(qr_code):
    """Get all scans for a specific QR code"""
    return qr_code.scans.all().order_by('-timestamp')


def get_user_scans(user):
    """Get all scans by a specific active user"""
    if not user.is_active:
        return ScanEvent.objects.none()
    return ScanEvent.objects.filter(scanned_by=user).order_by('-timestamp')


# ============= SCAN EVENT CRUD =============

def create_scan_event(qr_code, latitude, longitude, scan_type='arrival', scanned_by=None, device_info='', is_home_office=False, is_business_trip=False, actor_type=None, actor_email=None, actor_name=None, ip_address=None, request=None):
    """Create a new scan event"""
    scan = ScanEvent.objects.create(
        qr_code=qr_code,
        scanned_by=scanned_by,
        scan_type=scan_type,
        latitude=latitude,
        longitude=longitude,
        device_info=device_info,
        is_home_office=is_home_office,
        is_business_trip=is_business_trip
    )
    
    # Get address from coordinates
    address = None if 'test' in sys.argv else scan.get_address_from_coordinates()
    if address:
        scan.address = address
        scan.save()
    
    if actor_type and actor_email and actor_name:
        if is_home_office:
            scan_location = "Home Office"
        elif is_business_trip:
            scan_location = "Business Trip"
        else:
            scan_location = f'QR Code "{qr_code.name}"'
        log_action(
            actor_type=actor_type,
            actor_email=actor_email,
            actor_name=actor_name,
            action='create',
            message=f'{scan_type.capitalize()} scan at {scan_location}',
            ip_address=ip_address
        )
    
    # Send notifications based on company and manager settings
    # For home office and business trip scans, get company from scanned_by user
    company = scanned_by.company if (is_home_office or is_business_trip) else qr_code.company
    
    # Check which notification field to check based on scan type
    # Only arrival and departure have notification fields in models
    notification_field_map = {
        'arrival': 'notify_arrival',
        'departure': 'notify_departure',
    }
    
    notification_field = notification_field_map.get(scan_type)
    
    if notification_field and scanned_by:
        recipients = []
        
        # Check if company has notifications enabled for this scan type
        if getattr(company, notification_field, False):
            recipients.append(company.email)
        
        # Get all managers with notifications enabled for this scan type
        managers = User.objects.filter(
            company=company,
            is_active=True,
            is_manager=True,
            **{notification_field: True}
        )
        
        for manager in managers:
            if manager.email and manager.email not in recipients:
                recipients.append(manager.email)
        
        # Send email notifications if there are recipients
        if recipients:
            try:
                # Build dashboard URL
                dashboard_url = f"{settings.SITE_URL}/company/dashboard/" if hasattr(settings, 'SITE_URL') else '#'
                
                # Get language code from request or current active language
                language_code = 'sk'  # default fallback
                if request and hasattr(request, 'LANGUAGE_CODE'):
                    language_code = request.LANGUAGE_CODE
                else:
                    try:
                        language_code = get_language()
                    except:
                        pass
                
                # Prepare email context
                email_context = {
                    'scan_type': scan_type,
                    'user_name': scanned_by.name,
                    'timestamp': scan.timestamp,
                    'qr_name': 'Business Trip' if is_business_trip else ('Home Office' if is_home_office else qr_code.name),
                    'address': address or '',
                    'company_name': company.name,
                    'dashboard_url': dashboard_url,
                    'LANGUAGE_CODE': language_code
                }
                
                # Activate language for translations
                activate(language_code)
                
                # Render email HTML (pass request context for proper translation loading)
                html_message = render_to_string('scan_notification.html', email_context, request=request)
                
                # Email subject based on scan type (translated)
                subject_map = {
                    'arrival': f'✅ {scanned_by.name} - {_("Arrival")}',
                    'departure': f'🚪 {scanned_by.name} - {_("Departure")}',
                    'lunch_break_start': f'🍽️ {scanned_by.name} - {_("Lunch Break Started")}',
                    'lunch_break_end': f'✅ {scanned_by.name} - {_("Lunch Break Ended")}'
                }
                
                subject = subject_map.get(scan_type, f'{scanned_by.name} - Scan')
                
                # Send email
                send_mail(
                    subject=subject,
                    message='',  # Plain text fallback (empty because we use HTML)
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=recipients,
                    html_message=html_message,
                    fail_silently=True  # Don't raise exception if email fails
                )
            except Exception as e:
                # Log error but don't fail the scan creation
                print(f"Failed to send notification email: {str(e)}")
    
    return scan, address


# ============= VACATION CRUD =============

def create_vacation(user, date_from, date_to, time_from=None, time_to=None, vacation_type='vacation', approved=False, actor_type=None, actor_email=None, actor_name=None, ip_address=None, request=None):
    from datetime import datetime, time as dt_time
    
    # Convert strings to date objects if needed
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Convert time strings to time objects if needed
    if time_from and isinstance(time_from, str):
        try:
            time_from = datetime.strptime(time_from, '%H:%M').time()
        except:
            time_from = None
    if time_to and isinstance(time_to, str):
        try:
            time_to = datetime.strptime(time_to, '%H:%M').time()
        except:
            time_to = None
    
    # Validate dates
    if date_to < date_from:
        return None, str(_('End date cannot be before start date'))

    if (time_from and not time_to) or (time_to and not time_from):
        return None, str(_('Both time fields are required for a partial-day absence'))

    if date_from == date_to and time_from and time_to and time_to <= time_from:
        return None, str(_('End time must be after start time'))
    
    vacation = Vacation.objects.create(
        user=user,
        date_from=date_from,
        date_to=date_to,
        time_from=time_from,
        time_to=time_to,
        type=vacation_type,
        approved=approved
    )
    
    if actor_type and actor_email and actor_name:
        days = (date_to - date_from).days + 1
        log_action(
            actor_type=actor_type,
            actor_email=actor_email,
            actor_name=actor_name,
            action='create',
            message=f'Vacation ({vacation_type}) for "{user.name}" created: {date_from} to {date_to} ({days} days)',
            ip_address=ip_address
        )
    
    # Send notifications to company and managers with vacation notifications enabled
    company = user.company
    recipients = []
    
    # Check if company has vacation notifications enabled
    if company.notify_vacation:
        recipients.append(company.email)
    
    # Get all managers with vacation notifications AND can_edit_absences permission enabled
    managers = User.objects.filter(
        company=company,
        is_active=True,
        is_manager=True,
        notify_vacation=True,
        can_edit_absences=True  # Only managers who can edit absences
    )
    
    for manager in managers:
        if manager.email and manager.email not in recipients:
            recipients.append(manager.email)
    
    # Send email notifications if there are recipients
    if recipients:
        try:
            # Build dashboard URL from request with filters
            if request:
                from urllib.parse import quote
                # Get language code
                lang_code = getattr(request, 'LANGUAGE_CODE', 'sk')
                dashboard_url = request.build_absolute_uri(f'/{lang_code}/company/dashboard/?tab=absences&absence_employee_name={quote(user.name)}')
                # Build approval URL
                approval_url = request.build_absolute_uri(f'/{lang_code}/absence/{vacation.id}/approve/')
            else:
                dashboard_url = '#'
                approval_url = '#'
            
            # Get language code from request or current active language
            language_code = 'sk'  # default fallback
            if request and hasattr(request, 'LANGUAGE_CODE'):
                language_code = request.LANGUAGE_CODE
            else:
                try:
                    language_code = get_language()
                except:
                    pass
            
            # Calculate days count
            days_count = (date_to - date_from).days + 1
            
            # Prepare email context
            email_context = {
                'vacation_type': vacation_type,
                'user_name': user.name,
                'date_from': date_from,
                'date_to': date_to,
                'days_count': days_count,
                'approved': approved,
                'company_name': company.name,
                'dashboard_url': dashboard_url,
                'approval_url': approval_url,
                'vacation_id': vacation.id,
                'LANGUAGE_CODE': language_code
            }
            
            # Activate language for translations
            activate(language_code)
            
            # Render email HTML
            html_message = render_to_string('vacation_notification.html', email_context, request=request)
            
            # Email subject based on vacation type (translated)
            subject_map = {
                'vacation': f'🏖️ {user.name} - {_("Vacation Request")}',
                'sick_leave': f'🤒 {user.name} - {_("Sick Leave")}',
                'doctor': f'🏥 {user.name} - {_("Doctor Visit")}',
                'home_office': f'🏠 {user.name} - {_("Home Office")}'
            }
            
            subject = subject_map.get(vacation_type, f'📅 {user.name} - {_("Absence Request")}')
            
            # Send email
            send_mail(
                subject=subject,
                message='',  # Plain text fallback (empty because we use HTML)
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_message,
                fail_silently=True  # Don't raise exception if email fails
            )
        except Exception as e:
            # Log error but don't fail the vacation creation
            print(f"Failed to send vacation notification email: {str(e)}")
    
    return vacation, None


def update_vacation(vacation_id, company, user_id=None, date_from=None, date_to=None, time_from=None, time_to=None, vacation_type=None, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    from datetime import datetime
    try:
        vacation = Vacation.objects.get(id=vacation_id, user__company=company)
        changes = []
        
        if user_id:
            user = User.objects.get(id=user_id, company=company, is_active=True)
            old_user = vacation.user.name
            vacation.user = user
            changes.append(f'user from "{old_user}" to "{user.name}"')
        
        if date_from:
            vacation.date_from = date_from
            changes.append(f'date_from to {date_from}')
        
        if date_to:
            vacation.date_to = date_to
            changes.append(f'date_to to {date_to}')
        
        # Handle time fields
        if time_from is not None:  # Allow empty string to clear the field
            if time_from == '':
                vacation.time_from = None
                changes.append('time_from cleared')
            else:
                if isinstance(time_from, str):
                    try:
                        vacation.time_from = datetime.strptime(time_from, '%H:%M').time()
                        changes.append(f'time_from to {time_from}')
                    except:
                        pass
                else:
                    vacation.time_from = time_from
                    changes.append(f'time_from to {time_from}')
        
        if time_to is not None:  # Allow empty string to clear the field
            if time_to == '':
                vacation.time_to = None
                changes.append('time_to cleared')
            else:
                if isinstance(time_to, str):
                    try:
                        vacation.time_to = datetime.strptime(time_to, '%H:%M').time()
                        changes.append(f'time_to to {time_to}')
                    except:
                        pass
                else:
                    vacation.time_to = time_to
                    changes.append(f'time_to to {time_to}')
        
        if vacation_type:
            vacation.type = vacation_type
            changes.append(f'type to {vacation_type}')

        if vacation.date_to < vacation.date_from:
            return None, str(_('End date cannot be before start date'))

        if (vacation.time_from and not vacation.time_to) or (vacation.time_to and not vacation.time_from):
            return None, str(_('Both time fields are required for a partial-day absence'))

        if (
            vacation.date_from == vacation.date_to and
            vacation.time_from and
            vacation.time_to and
            vacation.time_to <= vacation.time_from
        ):
            return None, str(_('End time must be after start time'))
        
        vacation.save()
        
        if actor_type and actor_email and actor_name and changes:
            log_action(
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                action='update',
                message=f'Vacation for "{vacation.user.name}" updated: {", ".join(changes)}',
                ip_address=ip_address
            )
        
        return vacation, None
    except Vacation.DoesNotExist:
        return None, str(_('Vacation not found'))
    except User.DoesNotExist:
        return None, str(_('User not found'))


def delete_vacation(vacation_id, company, actor_type=None, actor_email=None, actor_name=None, ip_address=None, request=None, is_self_delete=False):
    from datetime import date
    try:
        vacation = Vacation.objects.get(id=vacation_id, user__company=company)
        user_name = vacation.user.name
        user_email = vacation.user.email
        date_from = vacation.date_from
        date_to = vacation.date_to
        vacation_type = vacation.type
        
        # Check if vacation is being cancelled before start date
        # Don't send email if user is deleting their own vacation
        current_date = date.today()
        send_cancellation_email = current_date < date_from and not is_self_delete
        
        vacation.is_active = False
        vacation.save()
        
        # Send cancellation email to employee if cancelled before start date
        if send_cancellation_email and user_email:
            try:
                # Build dashboard URL from request
                if request:
                    dashboard_url = request.build_absolute_uri('/user/dashboard/')
                else:
                    dashboard_url = '#'
                
                # Get language code from request
                language_code = 'sk'  # default fallback
                if request and hasattr(request, 'LANGUAGE_CODE'):
                    language_code = request.LANGUAGE_CODE
                else:
                    try:
                        language_code = get_language()
                    except:
                        pass
                
                # Calculate days count
                days_count = (date_to - date_from).days + 1
                
                # Prepare email context with cancelled status
                email_context = {
                    'vacation_type': vacation_type,
                    'user_name': user_name,
                    'date_from': date_from,
                    'date_to': date_to,
                    'days_count': days_count,
                    'approved': False,
                    'cancelled': True,
                    'company_name': company.name,
                    'dashboard_url': dashboard_url,
                    'LANGUAGE_CODE': language_code
                }
                
                # Activate language for translations
                activate(language_code)
                
                # Render email HTML
                html_message = render_to_string('vacation_notification.html', email_context, request=request)
                
                # Email subject
                subject = f'❌ {_("Vacation Request Cancelled")} - {date_from.strftime("%d.%m.%Y")} - {date_to.strftime("%d.%m.%Y")}'
                
                # Send email to employee
                send_mail(
                    subject=subject,
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user_email],
                    html_message=html_message,
                    fail_silently=True
                )
            except Exception as e:
                # Log error but don't fail the deletion
                print(f"Failed to send cancellation notification email: {str(e)}")
        
        if actor_type and actor_email and actor_name:
            log_action(
                actor_type=actor_type,
                actor_email=actor_email,
                actor_name=actor_name,
                action='delete',
                message=f'Vacation for "{user_name}" ({date_from} to {date_to}) deleted',
                ip_address=ip_address
            )
        
        return True, None
    except Vacation.DoesNotExist:
        return False, str(_('Vacation not found'))

