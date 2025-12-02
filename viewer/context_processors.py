from viewer.models import Company, User


def current_user_info(request):
    """Add current user/company info to all templates"""
    context = {
        'current_company': None,
        'current_user': None,
    }
    
    if request.session.get('user_type') == 'company' and 'company_id' in request.session:
        try:
            context['current_company'] = Company.objects.get(id=request.session['company_id'])
        except Company.DoesNotExist:
            pass
    
    elif request.session.get('user_type') == 'user' and 'user_id' in request.session:
        try:
            context['current_user'] = User.objects.get(id=request.session['user_id'])
        except User.DoesNotExist:
            pass
    
    return context
