from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from qr_reader_django import crud
import json

def check_email(request):
    """Check if email already exists in the system"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({'exists': False})
            
            # Check if email exists in User or Company model
            user_exists = crud.get_user_by_email(email) is not None
            company_exists = crud.get_company_by_email(email) is not None
            
            if user_exists or company_exists:
                return JsonResponse({
                    'exists': True,
                    'message': str(_('This email is already registered in the system'))
                })
            
            return JsonResponse({'exists': False})
            
        except Exception as e:
            return JsonResponse({'exists': False, 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)