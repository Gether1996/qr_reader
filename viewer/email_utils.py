from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import get_language, override


def normalize_language_code(language_code):
    if not language_code:
        return (getattr(settings, 'LANGUAGE_CODE', 'en') or 'en').split('-')[0].lower()
    return str(language_code).split('-')[0].lower()


def get_email_language_code(request=None, fallback=None):
    if request and getattr(request, 'LANGUAGE_CODE', None):
        return normalize_language_code(request.LANGUAGE_CODE)
    if fallback:
        return normalize_language_code(fallback)
    current_language = get_language()
    if current_language:
        return normalize_language_code(current_language)
    return normalize_language_code(getattr(settings, 'LANGUAGE_CODE', 'en'))


def render_localized_email(template_name, context=None, language_code=None, request=None):
    resolved_language = get_email_language_code(request=request, fallback=language_code)
    payload = dict(context or {})
    payload.setdefault('LANGUAGE_CODE', resolved_language)
    with override(resolved_language):
        return render_to_string(template_name, payload, request=request), resolved_language
