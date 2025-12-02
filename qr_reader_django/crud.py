from django.utils.translation import gettext_lazy as _
from viewer.models import Company, User, QRCodeProfile, ScanEvent

# ============= COMPANY CRUD =============

def create_company(name, email, password):
    """Create a new company"""
    if Company.objects.filter(email=email).exists():
        return None, str(_('Email already registered'))
    
    company = Company.objects.create(name=name, email=email)
    company.set_password(password)
    company.save()
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

def create_user(company, name, email, password):
    """Create a new user under a company"""
    if User.objects.filter(email=email).exists():
        return None, str(_('Email already exists'))
    
    user = User.objects.create(
        company=company,
        name=name,
        email=email
    )
    user.set_password(password)
    user.save()
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


def update_user(user_id, company, name=None, email=None, password=None, is_active=None):
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
        
        # Update status if provided
        if is_active is not None:
            user.is_active = is_active
        
        # Update password if provided
        if password:
            user.set_password(password)
        
        user.save()
        return user, None
    except User.DoesNotExist:
        return None, str(_('User not found'))


def delete_user(user_id, company):
    """Deactivate a user (soft delete)"""
    try:
        user = User.objects.get(id=user_id, company=company)
        user.is_active = False
        user.save()
        return True, None
    except User.DoesNotExist:
        return False, str(_('User not found'))


# ============= QR CODE CRUD =============

def create_qr_code(company, name, location, additional_info=''):
    """Create a new QR code"""
    qr_code = QRCodeProfile.objects.create(
        company=company,
        name=name,
        location=location,
        additional_info=additional_info
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


def deactivate_qr_code(qr_id, company):
    """Deactivate a QR code"""
    try:
        qr_code = QRCodeProfile.objects.get(id=qr_id, company=company)
        qr_code.is_active = False
        qr_code.save()
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

def create_scan_event(qr_code, latitude, longitude, scan_type='arrival', scanned_by=None, device_info=''):
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
    
    return scan, address
