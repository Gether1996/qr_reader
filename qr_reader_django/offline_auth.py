"""
Trakero – Offline Authentication

Provides HMAC-signed offline tokens that allow users to record attendance
scans without an active network connection. Tokens are issued to logged-in
users and stored in the browser's IndexedDB by offline-auth.js.

When syncing queued offline scans, the /user/offline-scan/ endpoint
validates the X-Offline-Token header instead of the usual CSRF + session.
"""

import base64
import hashlib
import hmac
import json
import time

from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from qr_reader_django import crud
from qr_reader_django.audit import get_client_ip

# Token lifetime: 60 days
TOKEN_TTL_SECONDS = 60 * 24 * 3600

VALID_SCAN_TYPES = {'arrival', 'departure', 'lunch_break_start', 'lunch_break_end'}


# ─── Token helpers ────────────────────────────────────────────────────────────

def _secret() -> bytes:
    return settings.SECRET_KEY.encode('utf-8')


def generate_offline_token(user_id: int, company_id: int, user_name: str) -> str:
    """
    Return a compact HMAC-SHA256-signed token.
    Format:  <base64url_payload>.<hex_signature>
    Payload: {"uid": int, "cid": int, "nam": str, "exp": unix_timestamp}
    """
    payload = {
        'uid': user_id,
        'cid': company_id,
        'nam': user_name,
        'exp': int(time.time()) + TOKEN_TTL_SECONDS,
    }
    payload_json = json.dumps(payload, separators=(',', ':'), sort_keys=True)
    payload_b64 = base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('ascii').rstrip('=')
    sig = hmac.new(_secret(), payload_b64.encode('ascii'), hashlib.sha256).hexdigest()
    return f'{payload_b64}.{sig}'


def verify_offline_token(token: str) -> dict | None:
    """
    Verify and decode a token.
    Returns the payload dict on success, None on failure or expiry.
    """
    if not token or '.' not in token:
        return None
    try:
        payload_b64, sig = token.rsplit('.', 1)
        expected = hmac.new(_secret(), payload_b64.encode('ascii'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        # Restore base64 padding
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += '=' * padding
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode('utf-8'))
        if payload.get('exp', 0) < time.time():
            return None
        return payload
    except Exception:
        return None


# ─── HTTP views ───────────────────────────────────────────────────────────────

@require_http_methods(['GET'])
def offline_token_view(request):
    """
    GET /api/offline-token/

    Session-authenticated endpoint that issues an offline token for the
    currently logged-in user.  Called automatically by offline-auth.js
    whenever the user is online so the token is always fresh.
    """
    if 'user_id' not in request.session or request.session.get('user_type') != 'user':
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'}, status=401)

    user = crud.get_user_by_id(request.session['user_id'])
    if not user or not user.is_active:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    token = generate_offline_token(user.id, user.company_id, user.name)
    return JsonResponse({
        'status': 'ok',
        'token': token,
        'user_id': user.id,
        'company_id': user.company_id,
        'user_name': user.name,
        'expires_in': TOKEN_TTL_SECONDS,
    })


@csrf_exempt
@require_http_methods(['POST'])
def offline_scan_view(request):
    """
    POST /<lang>/user/offline-scan/

    CSRF-exempt endpoint for uploading queued offline attendance scans.
    Authentication is via the X-Offline-Token request header; no active
    browser session is required.

    Request body is identical to user_scan_qr POST.
    """
    # ── Auth ──────────────────────────────────────────────────────────────────
    token_str = (
        request.headers.get('X-Offline-Token', '')
        or request.META.get('HTTP_X_OFFLINE_TOKEN', '')
    ).strip()

    if not token_str:
        return JsonResponse(
            {'status': 'error', 'message': str(_('Missing offline token'))},
            status=401,
        )

    claims = verify_offline_token(token_str)
    if not claims:
        return JsonResponse(
            {'status': 'error', 'message': str(_('Invalid or expired offline token'))},
            status=401,
        )

    user = crud.get_user_by_id(claims['uid'])
    if not user or not user.is_active:
        return JsonResponse(
            {'status': 'error', 'message': str(_('User not found or inactive'))},
            status=404,
        )

    # ── Parse body ────────────────────────────────────────────────────────────
    try:
        data = json.loads(request.body or b'{}')
    except (json.JSONDecodeError, ValueError):
        return JsonResponse(
            {'status': 'error', 'message': str(_('Invalid request payload'))},
            status=400,
        )

    # Re-use the enabled-buttons helper and scan-mode texts via lazy import
    # (avoids a circular import at module level since viewer.views imports crud)
    from viewer.account_texts import get_scan_mode_texts
    from viewer.views import _get_enabled_scan_buttons

    lang_code = getattr(request, 'LANGUAGE_CODE', 'en')
    scan_texts = get_scan_mode_texts(lang_code)

    uuid_val      = (data.get('uuid') or '').strip()
    latitude      = data.get('latitude')
    longitude     = data.get('longitude')
    scan_type     = data.get('scan_type', 'arrival')
    is_home_office  = bool(data.get('is_home_office', False))
    is_business_trip = bool(data.get('is_business_trip', False))
    is_no_qr      = bool(data.get('is_no_qr', False))

    # ── Validation ────────────────────────────────────────────────────────────
    if scan_type not in VALID_SCAN_TYPES:
        return JsonResponse(
            {'status': 'error', 'message': str(_('Invalid scan type'))},
            status=400,
        )

    if sum([is_home_office, is_business_trip, is_no_qr]) > 1:
        return JsonResponse(
            {'status': 'error', 'message': scan_texts['choose_one_mobile_mode']},
            status=400,
        )

    if latitude in (None, '') or longitude in (None, ''):
        return JsonResponse(
            {'status': 'error', 'message': str(_('Location is required'))},
            status=400,
        )

    try:
        latitude  = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return JsonResponse(
            {'status': 'error', 'message': str(_('Invalid location coordinates'))},
            status=400,
        )

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return JsonResponse(
            {'status': 'error', 'message': str(_('Location coordinates are out of range'))},
            status=400,
        )

    if not is_home_office and not is_business_trip and not is_no_qr and not uuid_val:
        return JsonResponse(
            {'status': 'error', 'message': str(_('UUID is required'))},
            status=400,
        )

    enabled_buttons = _get_enabled_scan_buttons(user)
    if scan_type not in enabled_buttons:
        return JsonResponse(
            {'status': 'error', 'message': str(_('This scan type is not available right now'))},
            status=409,
        )

    ip = get_client_ip(request)

    # ── Manual / no-QR modes ──────────────────────────────────────────────────
    if is_home_office or is_business_trip or is_no_qr:
        if is_home_office:
            scan_label = scan_texts['home_office']
        elif is_business_trip:
            scan_label = scan_texts['business_trip']
        else:
            scan_label = scan_texts['no_qr']

        scan, address = crud.create_scan_event(
            qr_code=None,
            scanned_by=user,
            latitude=latitude,
            longitude=longitude,
            scan_type=scan_type,
            device_info=request.META.get('HTTP_USER_AGENT', ''),
            is_home_office=is_home_office,
            is_business_trip=is_business_trip,
            is_no_qr=is_no_qr,
            actor_type='user',
            actor_email=user.email,
            actor_name=user.name,
            ip_address=ip,
            request=request,
        )
        return JsonResponse({
            'status': 'success',
            'message': str(_('{} scan recorded successfully!').format(scan_label)),
            'data': {
                'qr_name': str(scan_label),
                'qr_location': '',
                'scan_timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'scan_latitude': latitude,
                'scan_longitude': longitude,
                'scan_address': address or str(_('Address not available')),
            },
        })

    # ── QR-code scan ──────────────────────────────────────────────────────────
    qr_code = crud.get_qr_code_by_uuid(uuid_val)
    if not qr_code:
        return JsonResponse(
            {'status': 'error', 'message': str(_('QR code not found or inactive'))},
            status=404,
        )

    if qr_code.company != user.company:
        return JsonResponse(
            {'status': 'error', 'message': str(_('This QR code does not belong to your company'))},
            status=403,
        )

    scan, address = crud.create_scan_event(
        qr_code=qr_code,
        scanned_by=user,
        latitude=latitude,
        longitude=longitude,
        scan_type=scan_type,
        device_info=request.META.get('HTTP_USER_AGENT', ''),
        is_home_office=False,
        is_business_trip=False,
        is_no_qr=False,
        actor_type='user',
        actor_email=user.email,
        actor_name=user.name,
        ip_address=ip,
        request=request,
    )
    return JsonResponse({
        'status': 'success',
        'message': str(_('Scan recorded successfully!')),
        'data': {
            'qr_name': qr_code.name,
            'qr_location': qr_code.location or '',
            'scan_timestamp': scan.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'scan_latitude': latitude,
            'scan_longitude': longitude,
            'scan_address': address or str(_('Address not available')),
        },
    })
