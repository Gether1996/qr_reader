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
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

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
    """User model for users belonging to companies"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

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

        # Generate QR data content - URL to scan endpoint with UUID
        from django.conf import settings
        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
        qr_data = f"{base_url}/scan/{self.uuid}/"

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
    ]
    
    qr_code = models.ForeignKey(QRCodeProfile, on_delete=models.CASCADE, related_name='scans')
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='scans')
    scan_type = models.CharField(max_length=10, choices=SCAN_TYPE_CHOICES, default='arrival')
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=500, blank=True, null=True, help_text="Human-readable address")
    timestamp = models.DateTimeField(auto_now_add=True)
    device_info = models.TextField(blank=True, null=True, help_text="Browser/device information")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.qr_code.name} scanned at {self.timestamp}"
    
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