from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from viewer.models import Company, User
import json

def check_email(request):
    """Check if email already exists in the system"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({'exists': False})
            
            # Match the database unique constraints, including inactive records.
            user_exists = User.objects.filter(email=email).exists()
            company_exists = Company.objects.filter(email=email).exists()
            
            if user_exists or company_exists:
                return JsonResponse({
                    'exists': True,
                    'message': str(_('This email is already registered in the system'))
                })
            
            return JsonResponse({'exists': False})
            
        except Exception as e:
            return JsonResponse({'exists': False, 'error': str(e)})
    
    return JsonResponse({'status': 'error', 'message': str(_('Invalid request method'))}, status=400)
