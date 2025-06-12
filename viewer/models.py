import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
import hashlib
import time

class QRCodeProfile(models.Model):
    name_surname = models.CharField(max_length=255)
    id_card = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=255)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    uuid = models.CharField(max_length=20, unique=True, default=None, null=True, editable=False)
    created_at = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return self.name_surname

    def generate_short_uuid(self):
        seed = f"{self.id}-{time.time()}"
        return hashlib.sha1(seed.encode('utf-8')).hexdigest()[:20]

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = self.generate_short_uuid()

        # Generate QR data content
        qr_data = f"Name: {self.name_surname}\nEmail: {self.email}\nPhone: {self.phone}\nCompany: {self.company}\nIdCard: {self.id_card}\nUUID: {self.uuid}"

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
        file_name = f"qr_{self.name_surname.replace(' ', '_')}.png"
        self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)

class ScanEvent(models.Model):
    qr_code = models.ForeignKey(QRCodeProfile, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.qr_code.name_surname} scanned at {self.timestamp}"        