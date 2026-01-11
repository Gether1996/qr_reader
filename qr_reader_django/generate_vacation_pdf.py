import io
import os
from datetime import date, datetime, timedelta, time as dtime
from typing import Optional, Union

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.views.decorators.http import require_POST
from viewer.models import User


# ---------------- helpers ----------------

def _parse_date(value: Union[str, date, datetime]) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()

def _parse_time(value: Optional[Union[str, dtime]]) -> Optional[dtime]:
    if value is None:
        return None
    if isinstance(value, dtime):
        return value
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            pass
    raise ValueError(str(_("time_from/time_to must be time or string 'HH:MM' (or 'HH:MM:SS')")))

def _format_sk_date(d: date) -> str:
    return d.strftime("%d.%m.%Y")

def _format_sk_datetime(d: date, t: dtime) -> str:
    return datetime.combine(d, t).strftime("%d.%m.%Y %H:%M")

def _business_days_inclusive(d1: date, d2: date) -> int:
    if d2 < d1:
        d1, d2 = d2, d1
    cur = d1
    n = 0
    while cur <= d2:
        if cur.weekday() < 5:
            n += 1
        cur += timedelta(days=1)
    return n

def _ensure_font():
    """Ensure DejaVuSans font for Unicode characters (regular + bold)."""
    if "DejaVu" in pdfmetrics.getRegisteredFontNames() and "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames():
        return "DejaVu", "DejaVu-Bold"

    candidates_regular = [
        os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    candidates_bold = [
        os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    
    # Register regular
    for path in candidates_regular:
        if os.path.exists(path):
            try:
                if "DejaVu" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont("DejaVu", path))
                break
            except Exception:
                continue
    
    # Register bold
    for path in candidates_bold:
        if os.path.exists(path):
            try:
                if "DejaVu-Bold" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont("DejaVu-Bold", path))
                break
            except Exception:
                continue
    
    # Return registered fonts or fallback
    regular = "DejaVu" if "DejaVu" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    bold = "DejaVu-Bold" if "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    
    return regular, bold


# ---------------- main ----------------

def generate_dovolenka_pdf_response(
    *,
    user_id: int,
    date_from: Union[str, date, datetime],
    date_to: Union[str, date, datetime],
    time_from: Optional[Union[str, dtime]] = None,
    time_to: Optional[Union[str, dtime]] = None,
) -> HttpResponse:
    """
    Generate PDF form "VACATION" using template image and dynamic data.
    """
    user = User.objects.select_related("company").get(id=user_id)

    d_from = _parse_date(date_from)
    d_to = _parse_date(date_to)
    t_from = _parse_time(time_from)
    t_to = _parse_time(time_to)

    today = date.today()
    request_date = today - timedelta(days=14)

    if t_from and t_to:
        from_text = _format_sk_datetime(d_from, t_from)
        to_text = _format_sk_datetime(d_to, t_to)
    else:
        from_text = _format_sk_date(d_from)
        to_text = _format_sk_date(d_to)

    # Calculate working days
    if d_from == d_to and t_from and t_to:
        # Same date with times = half day
        work_days = 0.5
    else:
        # Normal working days calculation
        work_days = _business_days_inclusive(d_from, d_to)

    font_regular, font_bold = _ensure_font()

    # ========================================
    # LOAD TEMPLATE IMAGE
    # ========================================
    template_path = os.path.join(settings.BASE_DIR, "static", "images", "vzor_dovolenka.jpg")
    
    buf = io.BytesIO()
    # A5 landscape
    page_w, page_h = landscape(A5)
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))
    
    # Insert image as background
    img = ImageReader(template_path)
    c.drawImage(img, 0, 0, width=page_w, height=page_h, preserveAspectRatio=False)

    # ========================================
    # DYNAMIC DATA COORDINATES - CENTRAL CONFIGURATION
    # ========================================
    
    # Surname, name, title
    name_x = 130
    name_y = 340
    name_font_size = 10
    
    # Birth number
    rc_x = 510
    rc_y = 340
    rc_font_size = 10
    
    # Department (company) - format: "Company Name, Street Number, IČO" if available
    utvar_x = 68
    utvar_y = 308
    utvar_font_size = 9
    
    # Build company info string
    company_parts = []
    if user.company:
        company_parts.append(user.company.name)
        
        # Add address if street and street_number exist
        if user.company.street and user.company.street_number:
            company_parts.append(f"{user.company.street} {user.company.street_number}")
        
        # Add ZIP code if exists
        if user.company.zip_code:
            company_parts.append(user.company.zip_code)
        
        # Add state if exists
        if user.company.state:
            company_parts.append(user.company.state)
    
    company_info = ", ".join(company_parts) if company_parts else ""
    
    # Calendar year
    year_x = 326
    year_y = 291
    year_font_size = 10
    
    # Date FROM
    date_from_x = 85
    date_from_y = 267
    date_from_font_size = 8
    
    # Date TO
    date_to_x = 220
    date_to_y = 267
    date_to_font_size = 8
    
    # Number of working days
    work_days_x = 413
    work_days_y = 267
    work_days_font_size = 10
    
    # Request date
    request_date_x = 126
    request_date_y = 221
    request_date_font_size = 10
    
    # ========================================
    # WRITING DYNAMIC DATA
    # ========================================
    
    c.setFont(font_bold, name_font_size)
    c.drawString(name_x, name_y, user.name or "")
    
    if getattr(user, "rc", None):
        c.setFont(font_bold, rc_font_size)
        c.drawString(rc_x, rc_y, user.rc)
    
    c.setFont(font_bold, utvar_font_size)
    c.drawString(utvar_x, utvar_y, company_info)
    
    c.setFont(font_bold, year_font_size)
    c.drawString(year_x, year_y, str(d_from.year))
    
    c.setFont(font_bold, date_from_font_size)
    c.drawString(date_from_x, date_from_y, from_text)
    
    c.setFont(font_bold, date_to_font_size)
    c.drawString(date_to_x, date_to_y, to_text)
    
    c.setFont(font_bold, work_days_font_size)
    c.drawString(work_days_x, work_days_y, str(work_days))
    
    # Place of stay - empty, user can fill manually
    # c.drawString(miesto_x, miesto_y, "")
    
    c.setFont(font_bold, request_date_font_size)
    c.drawString(request_date_x, request_date_y, _format_sk_date(request_date))

    # Finish
    c.showPage()
    c.save()

    pdf = buf.getvalue()
    buf.close()

    filename = f"vacation_{user_id}_{d_from.isoformat()}_{d_to.isoformat()}.pdf"
    resp = HttpResponse(pdf, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp


@require_POST
def dovolenka_pdf(request):
    user_id = int(request.POST["user_id"])
    date_from = request.POST["date_from"]  # "YYYY-MM-DD"
    date_to = request.POST["date_to"]      # "YYYY-MM-DD"
    time_from = request.POST.get("time_from")  # "HH:MM" or None
    time_to = request.POST.get("time_to")

    return generate_dovolenka_pdf_response(
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        time_from=time_from or None,
        time_to=time_to or None,
    )
