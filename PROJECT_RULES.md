# PROJECT_RULES

## Project Overview

- Confirmed: This is a multilingual Django application for company attendance tracking and employee absence management.
- Confirmed: The main user roles are company accounts, manager employees, and regular employees.
- Confirmed: Core workflows include employee management, QR code location management, attendance scanning, absence requests/approval, attendance reporting, analytics, audit logs, and password setup/reset.
- Confirmed: There is a secondary `n8n_integration` area for workflow/webhook integrations that is separate from the main attendance product flow.

## Confirmed Architecture

- Backend framework: Django with function-based views.
- Primary apps:
  - `viewer/`: main product UI, templates, models, email rendering, dashboard behavior.
  - `qr_reader_django/`: project-level routing and business-logic modules (`crud.py`, domain-specific CRUD wrappers, auth flows, reports).
  - `n8n_integration/`: separate integration area for n8n workflows/webhooks.
- Frontend stack:
  - Django templates for HTML rendering.
  - Bootstrap-based layout/components.
  - Vanilla JavaScript in `static/scripts/`.
  - Shared app modal/toast helpers in `static/scripts/general.js`.
- Data storage:
  - MySQL in normal runtime.
  - In-memory SQLite when running tests.
- Authentication boundary:
  - Main app uses custom session-based auth with `company_id`, `user_id`, and `user_type` in session.
  - `n8n_integration` uses Django auth decorators and its own auth boundary.

## Core Module Responsibilities

- `viewer/models.py`
  - Defines the core business entities: `Company`, `User`, `QRCodeProfile`, `ScanEvent`, `Vacation`, password token models, `AuditLog`, and magazine models.
- `qr_reader_django/crud.py`
  - Central business logic for creating/updating/deleting companies, users, QR codes, scans, and absences.
  - Notification side effects and several business validations live here.
- `qr_reader_django/crud_user.py`, `crud_qr_code.py`, `crud_vacation.py`
  - HTTP/request-facing wrappers around business logic with permission checks and JSON responses.
- `viewer/views.py`
  - Dashboard rendering, scan flow validation, analytics, audit log display, settings, and password reset/setup views.
- `generate_pdf_excel.py`, `generate_vacation_pdf.py`
  - Reporting and document generation. Treat calculations here as business-sensitive.

## Core Business Workflows

### Attendance scanning

- Confirmed: Users scan attendance events through `user_scan_qr`.
- Confirmed: Allowed scan actions are stateful and determined by the latest scan history in `_get_enabled_scan_buttons`.
- Confirmed: The valid sequence is intentionally constrained:
  - Default state allows `arrival`.
  - After `arrival`, allowed actions are `departure` and `lunch_break_start`.
  - After `lunch_break_start`, allowed action is `lunch_break_end`.
  - After `lunch_break_end`, allowed actions are `departure` and `lunch_break_start`.
  - After `departure`, allowed action returns to `arrival`.
- Confirmed: Manual scan modes (`home_office`, `business_trip`, `no_qr`) are supported and treated as first-class attendance events in many calculations.
- Confirmed: Coordinates are required for scans, and normal QR scans must include a valid QR UUID from the same company.

### Employee management

- Confirmed: Company accounts can manage employees broadly.
- Confirmed: Manager employees can only manage employee records if `can_edit_employees` is true.
- Confirmed: Manager-specific permission flags are meaningful only when `is_manager` is true.
- Confirmed: Demoting a manager clears manager permissions and manager notification settings in update logic.

### QR code management

- Confirmed: Companies can create/edit/deactivate QR code profiles used for attendance scanning.
- Confirmed: Managers need `can_edit_qr_codes` for company-level QR administration.
- Confirmed: QR codes belong to a company and are enforced against cross-company usage.

### Absence workflow

- Confirmed: `Vacation` is the absence model for vacation/sick leave/doctor/other absence types.
- Confirmed: Regular users can create, edit, and delete only their own absences.
- Confirmed: Managers can act company-wide only when `can_edit_absences` is true.
- Confirmed: Managers without absence permission can still create absences for themselves only.
- Confirmed: Approval is a distinct workflow and should not be merged into generic create/update/delete behavior.
- Confirmed: Cancellation emails and approval emails are part of the business flow.

### Reporting and analytics

- Confirmed: Attendance reports calculate worked hours by pairing arrival/departure events and subtracting break time where applicable.
- Confirmed: Analytics compute current "at work" state from the latest scan type.
- Confirmed: QR-specific analytics and overall attendance analytics are not identical because manual modes are included in many totals but not in every QR-specific report.

## CRUD Rules That Must Not Change Without Explicit Approval

- Soft delete is intentional for:
  - `User`
  - `QRCodeProfile`
  - `Vacation`
- Existing filters rely on `is_active=True`. Do not convert these flows to hard deletes without explicit approval.
- Do not change manager/company/employee permission boundaries without explicit approval.
- Do not change scan sequencing rules without explicit approval.
- Do not change how worked hours, lunch breaks, or "currently at work" state are derived without explicit approval.
- Do not change absence approval/cancellation side effects without explicit approval.

## Localization Rules

- Confirmed: The project is multilingual and uses Django i18n.
- Confirmed: `LocaleMiddleware` is enabled and most routes are wrapped in `i18n_patterns`, so language prefixes are part of normal routing.
- Confirmed: Languages declared in settings are Slovak (`sk`), English (`en`), Spanish (`es`), and German (`de`).
- Confirmed: Translation files live under `locale/<lang>/LC_MESSAGES/django.po` and compiled `.mo` files are present.
- Confirmed: Template strings use `{% trans %}` / `{% blocktrans %}`.
- Confirmed: Python strings use Django translation helpers such as `gettext_lazy as _`.
- Confirmed: JavaScript-visible strings are exposed through `viewer/templates/translations_js.html` and consumed by scripts through the shared `translations` object and helper functions.
- Confirmed: Localized emails are rendered through `viewer/email_utils.py` using `override(language_code)`.
- Hard rule for future changes: Do not add user-visible strings directly into templates, Python, or JavaScript without following the existing translation pipeline.

## Datetime Rules

- Confirmed: `USE_TZ = False` in settings, with an explicit code comment stating the project uses standard datetime values only.
- Confirmed: The codebase primarily uses naive `datetime.now()`, `datetime.strptime(...)`, and date comparisons without timezone conversions.
- Confirmed: Token expiration checks, attendance calculations, absence validation, analytics, and report generation all rely on naive datetime/date behavior.
- Confirmed: Frontend filters and report inputs use date strings such as `YYYY-MM-DD`, and UI display formats are localized separately.
- Hard rule for future changes: Do not introduce timezone conversion logic unless a specific existing feature already requires it in that exact area.

## Mobile / Responsive UI Rules

- Confirmed: Mobile support is an existing product requirement, not an afterthought.
- Confirmed: The scan experience is mobile-first and has dedicated responsive styling in `static/css/user_scan_qr.css`.
- Confirmed: The company dashboard uses separate desktop table and mobile card layouts rather than forcing tables onto small screens.
- Confirmed: Reusable filter and pagination UI preserve state across mobile and desktop flows.
- Hard rule for future changes:
  - Prefer mobile-safe layouts first.
  - Avoid introducing desktop-only tables/modals/forms when an existing mobile card or stacked pattern should be reused.
  - Preserve both desktop and mobile usability, but optimize for phone screens first.

## API / Data Flow Conventions

- Confirmed: Views usually orchestrate request parsing, authentication/session checks, filtering, and rendering.
- Confirmed: Core write-side business behavior is concentrated in `qr_reader_django/crud.py`.
- Confirmed: Domain-specific request modules (`crud_user.py`, `crud_qr_code.py`, `crud_vacation.py`) wrap business logic with permission enforcement and JSON responses.
- Confirmed: Frontend JavaScript often performs AJAX POST requests to language-prefixed endpoints and then reloads or updates the page state.
- Confirmed: CSRF tokens and language prefixes are injected globally in the base template for frontend use.

## Reusable Components and Patterns

- Reuse `filters_card.html` for filter controls and persisted query-state patterns when possible.
- Reuse `paginator.html` for paginated list behavior.
- Reuse `static/scripts/general.js` for dialogs, confirmations, and toasts instead of introducing a parallel notification system.
- Reuse the translations object from `translations_js.html` for JavaScript UI text.
- Reuse existing permission checks and session helpers instead of introducing alternate authorization flows inside the core app.
- For public-facing and shared UI styling, also follow `STYLE_RULES.md`.

## Risky Areas / Do Not Change Without Explicit Approval

- `_get_enabled_scan_buttons` and `user_scan_qr` validation flow.
- Manager permission semantics and their interaction with notification flags.
- Soft-delete behavior and any query filtering that depends on `is_active`.
- Attendance hour calculations in analytics and report generation.
- Vacation validation rules for date order, partial-day times, and approval/cancellation behavior.
- Password token validity behavior and existing password policy differences between company reset and employee setup.
- Any localization plumbing that affects translated templates, JavaScript strings, or email rendering.
- The auth boundary difference between the main app and `n8n_integration`.

## Safe Change Guidelines

- Prefer narrow changes over refactors.
- Assume business logic is intentional unless the code clearly proves otherwise.
- If a requested change touches attendance sequencing, approval flow, permission boundaries, reporting math, or deletion behavior, pause and confirm before changing behavior.
- Before adding new UI or helpers, check whether an existing template partial, script helper, or CSS pattern already covers the need.
- Before changing user-visible text, update translations consistently across the existing i18n system.

## Open Questions / Assumptions

- Assumption: The magazine-related models and views are a secondary product feature and not part of the core attendance workflow. This appears true from structure, but it was not fully traced end-to-end.
- Assumption: English acts mainly as the source-string language while Slovak is the primary configured default language.
- Open question: There may be additional business intent in unreviewed templates/scripts that reinforce current UI behavior, so any broad UI rewrite should still be preceded by a targeted scan of the affected area.
