from django.http import JsonResponse
from viewer.models import QRCodeProfile, ScanEvent
import json
from datetime import datetime

def add_qr_code(request):
    if request.method == 'POST':
        json_data = json.loads(request.body.decode('utf-8'))

        new_qr_code = QRCodeProfile.objects.create(
            name_surname=json_data.get('name'),
            id_card=json_data.get('id_card') if json_data.get('id_card') else "",
            email=json_data.get('email') if json_data.get('email') else "",
            phone =json_data.get('phone') if json_data.get('phone') else "",
            company =json_data.get('company') if json_data.get('company') else "",
            created_at=datetime.now(),
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Nesprávny request.'})

def record_scan(request, qr_uuid):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            qr_profile = QRCodeProfile.objects.get(uuid=qr_uuid)
            ScanEvent.objects.create(qr_code=qr_profile, latitude=latitude, longitude=longitude)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)