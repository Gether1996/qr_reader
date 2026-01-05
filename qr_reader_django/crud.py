from django.utils.translation import gettext_lazy as _
from viewer.models import Company, User, QRCodeProfile, ScanEvent, Vacation
from datetime import datetime
from qr_reader_django.audit import log_action

# ============= COMPANY CRUD =============

def create_company(name, email, password, auto_lunch_breaks=False, ip_address=None):
    """Create a new company"""
    if Company.objects.filter(email=email).exists():
        return None, str(_('Email already registered'))
    
    company = Company.objects.create(name=name, email=email, auto_lunch_breaks=auto_lunch_breaks)
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

def create_user(company, name, email, password, basic_work_hours=160, holidays_per_year=20, is_manager=False, can_edit_employees=False, can_edit_qr_codes=False, can_edit_absences=False, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Create a new user under a company"""
    if User.objects.filter(email=email).exists():
        return None, str(_('Email already exists'))
    
    user = User.objects.create(
        company=company,
        name=name,
        email=email,
        working_hours=basic_work_hours,
        holidays_per_year=holidays_per_year,
        is_manager=is_manager,
        can_edit_employees=can_edit_employees if is_manager else False,
        can_edit_qr_codes=can_edit_qr_codes if is_manager else False,
        can_edit_absences=can_edit_absences if is_manager else False
    )
    user.set_password(password)
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


def update_user(user_id, company, name=None, email=None, password=None, basic_work_hours=None, holidays_per_year=None, is_active=None, is_manager=None, can_edit_employees=None, can_edit_qr_codes=None, can_edit_absences=None, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Update user details"""
    try:
        user = User.objects.get(id=user_id, company=company)
        
        # Check if email is being changed and if it already exists
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                return None, str(_('Email already exists'))
            user.email = email
        
        # Update name if provided
        if name:
            user.name = name
        
        # Update basic work hours if provided
        if basic_work_hours is not None:
            user.working_hours = basic_work_hours
        
        # Update holidays per year if provided
        if holidays_per_year is not None:
            user.holidays_per_year = holidays_per_year
        
        # Update manager status if provided
        if is_manager is not None:
            user.is_manager = is_manager
            # If changing from manager to employee, remove all permissions
            if not is_manager:
                user.can_edit_employees = False
                user.can_edit_qr_codes = False
                user.can_edit_absences = False
        
        # Update permissions if provided (only if user is manager)
        if user.is_manager:
            if can_edit_employees is not None:
                user.can_edit_employees = can_edit_employees
            if can_edit_qr_codes is not None:
                user.can_edit_qr_codes = can_edit_qr_codes
            if can_edit_absences is not None:
                user.can_edit_absences = can_edit_absences
        
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
            if email and email != user.email: changes.append(f'email to "{email}"')
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

def create_scan_event(qr_code, latitude, longitude, scan_type='arrival', scanned_by=None, device_info='', actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    """Create a new scan event"""
    scan = ScanEvent.objects.create(
        qr_code=qr_code,
        scanned_by=scanned_by,
        scan_type=scan_type,
        latitude=latitude,
        longitude=longitude,
        device_info=device_info
    )
    
    # Get address from coordinates
    address = scan.get_address_from_coordinates()
    if address:
        scan.address = address
        scan.save()
    
    if actor_type and actor_email and actor_name:
        log_action(
            actor_type=actor_type,
            actor_email=actor_email,
            actor_name=actor_name,
            action='create',
            message=f'{scan_type.capitalize()} scan at QR Code "{qr_code.name}"',
            ip_address=ip_address
        )
    
    return scan, address


# ============= VACATION CRUD =============

def create_vacation(user, date_from, date_to, vacation_type='vacation', approved=False, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    from datetime import datetime
    
    # Convert strings to date objects if needed
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Validate dates
    if date_to < date_from:
        return None, str(_('End date cannot be before start date'))
    
    vacation = Vacation.objects.create(
        user=user,
        date_from=date_from,
        date_to=date_to,
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
    
    return vacation, None


def update_vacation(vacation_id, company, user_id=None, date_from=None, date_to=None, vacation_type=None, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
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
        
        if vacation_type:
            vacation.type = vacation_type
            changes.append(f'type to {vacation_type}')
        
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


def delete_vacation(vacation_id, company, actor_type=None, actor_email=None, actor_name=None, ip_address=None):
    try:
        vacation = Vacation.objects.get(id=vacation_id, user__company=company)
        user_name = vacation.user.name
        date_from = vacation.date_from
        date_to = vacation.date_to
        vacation.is_active = False
        vacation.save()
        
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

