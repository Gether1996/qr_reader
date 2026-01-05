"""
Audit logging utility for tracking all CRUD operations
"""
from viewer.models import AuditLog


def log_action(actor_type, actor_email, actor_name, action, message, ip_address=None):
    """
    Create an audit log entry
    
    Args:
        actor_type: 'company' or 'user'
        actor_email: Email of the actor
        actor_name: Name of the actor (company name or user name)
        action: 'create', 'update', 'delete', 'approve', 'login', 'logout'
        message: Descriptive message of what happened
        ip_address: IP address of the request (optional)
    """
    try:
        AuditLog.objects.create(
            actor_type=actor_type,
            actor_email=actor_email,
            actor_name=actor_name,
            action=action,
            message=message,
            ip_address=ip_address
        )
    except Exception as e:
        # Log to console but don't fail the operation
        print(f"Audit log error: {e}")


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
