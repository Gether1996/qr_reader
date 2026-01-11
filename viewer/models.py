import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import requests
import uuid as uuid_lib

class Company(models.Model):
    """Company model for company authentication and QR code management"""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    # Optional company details
    ico = models.CharField(max_length=50, blank=True, null=True, default=None, help_text="IČO - Identifikačné číslo organizácie")
    dic = models.CharField(max_length=50, blank=True, null=True, default=None, help_text="DIČ - Daňové identifikačné číslo")
    phone = models.CharField(max_length=50, blank=True, null=True, default=None, help_text="Telefón")
    street = models.CharField(max_length=255, blank=True, null=True, default=None, help_text="Ulica")
    street_number = models.CharField(max_length=50, blank=True, null=True, default=None, help_text="Číslo domu")
    zip_code = models.CharField(max_length=20, blank=True, null=True, default=None, help_text="PSČ")
    city = models.CharField(max_length=255, blank=True, null=True, default=None, help_text="Mesto")
    state = models.CharField(max_length=255, blank=True, null=True, default=None, help_text="Štát")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    auto_lunch_breaks = models.BooleanField(default=False)
    notification_company = models.BooleanField(default=False)
    notify_arrival = models.BooleanField(default=False)
    notify_departure = models.BooleanField(default=False)
    notify_vacation = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if provided password matches stored hash"""
        return check_password(raw_password, self.password)


class User(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    rc = models.CharField(max_length=20, blank=True, null=True, default=None) # rodné číslo
    phone = models.CharField(max_length=20, blank=True, null=True, default=None)
    birth_date = models.DateField(blank=True, null=True, default=None)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    working_hours = models.IntegerField(default=160)
    has_lunch_break = models.BooleanField(default=True)
    lunch_break_duration = models.IntegerField(default=30)
    holidays_per_year = models.IntegerField(default=20)
    is_manager = models.BooleanField(default=False)
    can_edit_employees = models.BooleanField(default=False)
    can_edit_qr_codes = models.BooleanField(default=False)
    can_edit_absences = models.BooleanField(default=False)
    notifications = models.BooleanField(default=False)
    notify_arrival = models.BooleanField(default=False)
    notify_departure = models.BooleanField(default=False)
    notify_vacation = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if provided password matches stored hash"""
        return check_password(raw_password, self.password)


class QRCodeProfile(models.Model):
    """QR Code profiles created by companies"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='qr_codes')
    name = models.CharField(max_length=255, help_text="Name for this QR code")
    location = models.CharField(max_length=500, help_text="Location/description")
    additional_info = models.TextField(blank=True, null=True, help_text="Any additional information")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    uuid = models.CharField(max_length=36, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.company.name}"

    def generate_uuid(self):
        """Generate a unique UUID for the QR code"""
        return str(uuid_lib.uuid4())

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = self.generate_uuid()

        # Generate QR data content - just the UUID (scanned via user app)
        qr_data = self.uuid

        # Generate the QR code image
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save to an in-memory file
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Save the image to the model
        file_name = f"qr_{self.uuid}.png"
        self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)


class ScanEvent(models.Model):
    """Log of QR code scans with location and timestamp"""
    SCAN_TYPE_CHOICES = [
        ('arrival', 'Príchod'),
        ('departure', 'Odchod'),
        ('lunch_break_start', 'Prestávka začiatok'),
        ('lunch_break_end', 'Prestávka koniec'),
    ]
    
    qr_code = models.ForeignKey(QRCodeProfile, on_delete=models.CASCADE, related_name='scans', null=True, blank=True)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scans')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES, default='arrival')
    is_home_office = models.BooleanField(default=False, help_text="Indicates if this is a home office scan")
    is_business_trip = models.BooleanField(default=False, help_text="Indicates if this is a business trip scan")
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=500, blank=True, null=True, help_text="Human-readable address")
    timestamp = models.DateTimeField(auto_now_add=True)
    device_info = models.TextField(blank=True, null=True, help_text="Browser/device information")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        if self.is_home_office:
            return f"Home Office scan at {self.timestamp}"
        if self.is_business_trip:
            return f"Business Trip scan at {self.timestamp}"
        return f"{self.qr_code.name if self.qr_code else 'Unknown'} scanned at {self.timestamp}"
    
    def get_address_from_coordinates(self):
        """Reverse geocode coordinates to get human-readable address"""
        try:
            # Using Nominatim (OpenStreetMap) - free and no API key required
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': self.latitude,
                'lon': self.longitude,
                'format': 'json',
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'QRReaderApp/1.0'  # Required by Nominatim
            }
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                address_parts = data.get('address', {})
                
                # Build address string
                address_components = []
                
                # Street
                road = address_parts.get('road') or address_parts.get('street')
                house_number = address_parts.get('house_number')
                if road:
                    if house_number:
                        address_components.append(f"{road} {house_number}")
                    else:
                        address_components.append(road)
                
                # City/Town
                city = (address_parts.get('city') or 
                       address_parts.get('town') or 
                       address_parts.get('village') or
                       address_parts.get('municipality'))
                postcode = address_parts.get('postcode')
                
                if postcode and city:
                    address_components.append(f"{postcode} {city}")
                elif city:
                    address_components.append(city)
                elif postcode:
                    address_components.append(postcode)
                
                # Country
                country = address_parts.get('country')
                if country:
                    address_components.append(country)
                
                return ', '.join(address_components) if address_components else None
                
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None


class Vacation(models.Model):
    """Vacation/time-off records for users (managed by company)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacations')
    date_from = models.DateField(help_text="Start date of vacation")
    date_to = models.DateField(help_text="End date of vacation")
    time_from = models.TimeField(blank=True, null=True, default=None)
    time_to = models.TimeField(blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=100, default=None, blank=True, null=True)
    approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_from']
    
    def __str__(self):
        return f"{self.user.name}: {self.date_from} - {self.date_to}"
    
    @property
    def days_count(self):
        """Calculate number of days in vacation"""
        if self.date_from and self.date_to:
            # If same day and has time_from and time_to, it's half day
            if self.date_from == self.date_to and self.time_from and self.time_to:
                return 0.5
            return (self.date_to - self.date_from).days + 1
        return 0

# ============= PASSWORD RESET MODEL =============

class PasswordResetToken(models.Model):
    """Password reset tokens for companies"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Reset token for {self.company.name}"
    
    def is_valid(self):
        """Check if token is still valid"""
        from datetime import datetime
        return not self.is_used and datetime.now() < self.expires_at.replace(tzinfo=None)


# ============= AUDIT LOG MODEL =============

class AuditLog(models.Model):
    """Audit log for tracking all CRUD operations"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    ACTOR_TYPE_CHOICES = [
        ('company', 'Company'),
        ('user', 'User'),
    ]
    
    # Who performed the action
    actor_type = models.CharField(max_length=10, choices=ACTOR_TYPE_CHOICES)
    actor_email = models.EmailField()
    actor_name = models.CharField(max_length=255)
    
    # What was done
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    message = models.TextField()
    
    # When
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['actor_email']),
        ]
    
    def __str__(self):
        return f"{self.actor_name} ({self.actor_type}) - {self.action} at {self.timestamp}"




##################################################

# ============= MAGAZINE MODELS =============

class Magazine(models.Model):
    """Magazine model - represents a magazine issue"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='magazines')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_magazines')
    
    # Magazine Configuration
    title = models.CharField(max_length=255, default="My Magazine")
    issue_number = models.CharField(max_length=50, default="1")
    tagline = models.CharField(max_length=255, blank=True, null=True, default="An awesome magazine")
    publish_date = models.DateField()
    
    # Theme & Design
    template_id = models.CharField(max_length=50, default="classic")
    primary_font = models.CharField(max_length=100, default="Playfair Display")
    secondary_font = models.CharField(max_length=100, default="Lato")
    primary_color = models.CharField(max_length=20, default="#1a1a1a")
    secondary_color = models.CharField(max_length=20, default="#666666")
    background_color = models.CharField(max_length=20, default="#1a1a1a")
    text_color = models.CharField(max_length=20, default="#1a1a1a")
    cover_background_image = models.URLField(max_length=500, blank=True, null=True, default="/static/images/pozadie_1.jpg")  # URL to cover background image
    cover_header_position = models.CharField(max_length=20, default="top", choices=[
        ('top', 'Top'),
        ('center', 'Center'),
        ('bottom', 'Bottom')
    ])  # Position of header on cover page
    
    # Settings
    language = models.CharField(max_length=5, default="en")
    print_bleed = models.BooleanField(default=False)
    categories = models.TextField(default="News,Features,Opinion,Culture,Sports")  # Comma-separated
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-modified_at']
    
    def __str__(self):
        return f"{self.title} - Issue {self.issue_number}"
    
    def get_categories_list(self):
        """Return categories as a list"""
        return [cat.strip() for cat in self.categories.split(',') if cat.strip()]


class MagazineArticle(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Koncept'),
        ('published', 'Publikovaný'),
    ]

    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE, related_name='articles')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    
    # Article Content
    title = models.CharField(max_length=500)
    teaser = models.TextField(blank=True, null=True, help_text="Short teaser for cover/TOC", default="Teaser text")
    category = models.CharField(max_length=100)
    
    # Cover Story
    is_main_story = models.BooleanField(default=False)
    is_secondary_story = models.BooleanField(default=False)
    cover_image = models.ImageField(upload_to='magazine_images/', blank=True, null=True)
    header_image = models.ImageField(upload_to='magazine_headers/', blank=True, null=True, help_text="Image displayed in article header")
    
    # Layout
    page_number = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Order in magazine")
    
    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['magazine', 'order', 'page_number']
    
    def __str__(self):
        return f"{self.title} - {self.magazine.title}"


class ContentBlock(models.Model):
    """Content blocks for articles - can be text or images"""
    BLOCK_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
    ]
    
    ALIGNMENT_CHOICES = [
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
        ('justify', 'Justify'),
    ]
    
    FONT_SIZE_CHOICES = [
        ('sm', 'Small'),
        ('base', 'Base'),
        ('lg', 'Large'),
        ('xl', 'Extra Large'),
    ]
    
    article = models.ForeignKey(MagazineArticle, on_delete=models.CASCADE, related_name='content_blocks')
    block_type = models.CharField(max_length=10, choices=BLOCK_TYPE_CHOICES)
    order = models.IntegerField(default=0)
    
    # Text content
    text_content = models.TextField(blank=True, null=True)
    
    # Image content
    image = models.ImageField(upload_to='magazine_content/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    image_caption = models.CharField(max_length=500, blank=True, null=True)
    
    # Styling
    font_family = models.CharField(max_length=100, blank=True, null=True)
    font_size = models.CharField(max_length=10, choices=FONT_SIZE_CHOICES, blank=True, null=True)
    text_color = models.CharField(max_length=20, blank=True, null=True)
    background_color = models.CharField(max_length=20, blank=True, null=True)
    alignment = models.CharField(max_length=10, choices=ALIGNMENT_CHOICES, default='left')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['article', 'order']
    
    def __str__(self):
        return f"{self.block_type} block for {self.article.title}"