from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import get_language, override
from urllib.parse import urljoin, urlparse


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


def _normalize_base_url(raw_url):
    if not raw_url:
        return ''

    parsed = urlparse(str(raw_url).strip())
    if not parsed.scheme or not parsed.netloc:
        return ''

    return f'{parsed.scheme}://{parsed.netloc}'


def _is_local_hostname(hostname):
    host = (hostname or '').split(':', 1)[0].lower()
    return host in {'localhost', '127.0.0.1', '0.0.0.0', 'web'}


def get_public_base_url(request=None):
    configured_site_url = _normalize_base_url(getattr(settings, 'SITE_URL', ''))
    configured_site_is_public = False
    if configured_site_url:
        configured_site_is_public = not _is_local_hostname(urlparse(configured_site_url).hostname)

    candidates = []
    if request:
        for header_name in ('HTTP_ORIGIN', 'HTTP_REFERER'):
            header_value = request.META.get(header_name)
            normalized_header = _normalize_base_url(header_value)
            if normalized_header:
                candidates.append(normalized_header)

        forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST')
        if forwarded_host:
            forwarded_host = forwarded_host.split(',')[0].strip()

        forwarded_proto = request.META.get('HTTP_X_FORWARDED_PROTO')
        if forwarded_proto:
            forwarded_proto = forwarded_proto.split(',')[0].strip()

        request_host = forwarded_host or request.get_host()
        request_scheme = forwarded_proto or request.scheme
        if request_host and request_scheme:
            candidates.append(f'{request_scheme}://{request_host}')

    if configured_site_url:
        candidates.append(configured_site_url)

    seen = set()
    for candidate in candidates:
        normalized_candidate = _normalize_base_url(candidate)
        if not normalized_candidate or normalized_candidate in seen:
            continue
        seen.add(normalized_candidate)

        if configured_site_is_public and _is_local_hostname(urlparse(normalized_candidate).hostname):
            continue

        return normalized_candidate

    return configured_site_url


def build_public_url(request=None, path=''):
    base_url = get_public_base_url(request=request)
    relative_path = f"/{str(path or '').lstrip('/')}"
    return urljoin(f'{base_url.rstrip("/")}/', relative_path.lstrip('/')) if base_url else relative_path


def render_localized_email(template_name, context=None, language_code=None, request=None):
    resolved_language = get_email_language_code(request=request, fallback=language_code)
    payload = dict(context or {})
    payload.setdefault('LANGUAGE_CODE', resolved_language)
    with override(resolved_language):
        return render_to_string(template_name, payload, request=request), resolved_language
