from django.shortcuts import render
from viewer.models import QRCodeProfile

def homepage(request):
    qr_codes = QRCodeProfile.objects.all()
    return render(request, 'homepage.html', {'qr_codes': qr_codes})