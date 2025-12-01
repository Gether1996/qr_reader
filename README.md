# QR Reader System - Reworked

A Django-based QR code management system with company and user authentication, QR code generation, and scan tracking with GPS locations.

## Features

- **Company Authentication**: Companies can register and login to manage QR codes
- **User Management**: Companies can register users under their account
- **QR Code Generation**: Create custom QR codes with name, location, and additional info
- **Scan Tracking**: Every scan is logged with exact GPS coordinates and timestamp
- **Responsive Dashboard**: Modern UI for managing QR codes and viewing scan history
- **Admin Panel**: Full Django admin interface for system management

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Quick Start

1. **Clone/Navigate to the project directory**
   ```bash
   cd qr_reader
   ```

2. **Activate virtual environment** (if not already active)
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Run the setup script**
   ```powershell
   .\setup.ps1
   ```
   
   This will:
   - Backup your old database (if exists)
   - Run database migrations
   - Optionally create a Django admin superuser

4. **Start the development server**
   ```bash
   python manage.py runserver
   ```

5. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Manual Setup (Alternative)

If you prefer to set up manually:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt

# Backup old database (optional)
copy db.sqlite3 db.sqlite3.backup

# Remove old database to start fresh
rm db.sqlite3

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Start server
python manage.py runserver
```

## Project Structure

```
qr_reader/
├── viewer/                  # Main app
│   ├── models.py           # Company, User, QRCodeProfile, ScanEvent models
│   ├── views.py            # All views (auth, dashboards, QR management)
│   ├── admin.py            # Admin interface configuration
│   └── templates/          # HTML templates
│       ├── base_new.html
│       ├── landing.html
│       ├── company_login.html
│       ├── company_register.html
│       ├── company_dashboard.html
│       ├── user_login.html
│       ├── user_dashboard.html
│       ├── qr_scans.html
│       └── scan_qr.html
├── qr_reader_django/       # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/                 # Static files (CSS, JS, images)
├── media/                  # Uploaded files (QR codes)
└── manage.py
```

## Usage

### For Companies

1. **Register**: Go to the homepage and click "Register Company"
2. **Login**: Use your company email and password
3. **Create QR Codes**: 
   - Click "Create QR Code" in the dashboard
   - Enter name, location, and optional additional info
   - QR code is generated automatically
4. **Register Users**: 
   - Click "Register User" 
   - Add user name, email, and password
5. **View Scans**: Click on any QR code to see all scan events with locations

### For Users

1. **Login**: Use credentials provided by your company
2. **View QR Codes**: See all active QR codes from your company
3. **View Scans**: Monitor scan history for all company QR codes

### Scanning QR Codes

When someone scans a QR code:
1. They are redirected to a scan page
2. Browser requests location permission
3. Scan is recorded with GPS coordinates and timestamp
4. If user is logged in, their identity is also recorded

## Models

### Company
- name
- email (unique)
- password (hashed)
- created_at
- is_active

### User
- company (ForeignKey)
- name
- email (unique)
- password (hashed)
- created_at
- is_active

### QRCodeProfile
- company (ForeignKey)
- name
- location
- additional_info
- qr_code (image)
- uuid (unique)
- created_at
- is_active

### ScanEvent
- qr_code (ForeignKey)
- scanned_by (ForeignKey to User, optional)
- latitude
- longitude
- timestamp
- device_info

## API Endpoints

- `/` - Landing page
- `/company/register/` - Company registration
- `/company/login/` - Company login
- `/company/dashboard/` - Company dashboard
- `/user/login/` - User login
- `/user/dashboard/` - User dashboard
- `/qr/create/` - Create QR code (POST)
- `/qr/scans/<id>/` - View QR code scans
- `/user/create/` - Register user (POST)
- `/scan/<uuid>/` - Public QR code scan page

## Technologies Used

- **Backend**: Django 5.2.3
- **Database**: SQLite
- **Frontend**: Bootstrap 5, jQuery, SweetAlert2, Font Awesome
- **QR Generation**: qrcode library with Pillow
- **Location**: Browser Geolocation API

## Security Notes

- Passwords are hashed using Django's password hashers
- CSRF protection on all forms
- Session-based authentication
- Location permission required for scanning

## Customization

### Change Base URL
Edit `qr_reader_django/settings.py`:
```python
BASE_URL = 'https://yourdomain.com'
```

### Styling
Modify templates in `viewer/templates/` or add custom CSS in `static/css/`

## Troubleshooting

**Issue**: Migrations not applying
```bash
python manage.py migrate --run-syncdb
```

**Issue**: Old data conflicts
```bash
# Delete database and start fresh
rm db.sqlite3
python manage.py migrate
```

**Issue**: Static files not loading
```bash
python manage.py collectstatic
```

## Future Enhancements

- [ ] Email verification for company registration
- [ ] Password reset functionality
- [ ] Export scan data to CSV/Excel
- [ ] Analytics dashboard with charts
- [ ] Mobile app for scanning
- [ ] Bulk QR code generation
- [ ] Custom QR code designs
- [ ] API for external integrations

## License

This project is for educational/personal use.

## Support

For issues or questions, please check the code comments or Django documentation.
