# ðŸ“± Trakero - Attendance Management System

## ðŸŒŸ Overview

Advanced web-based attendance and workforce management system using QR code technology. Perfect for companies of any size looking to modernize their employee time tracking, vacation management, and workplace analytics.

## âœ¨ Key Features

### ðŸ‘” Company Management
- **Multi-Company Support** - Each company has its own isolated environment
- **Company Dashboard** - Centralized control panel for all operations
- **Company Settings** - Customizable work policies and notification preferences
- **Role-Based Access** - Company owners and managers with granular permissions

### ðŸ‘¥ Employee Management
- **Employee Registration** - Create and manage employee accounts
- **Manager Roles** - Assign managers with specific permissions:
  - `can_edit_employees` - Manage employee data
  - `can_edit_qr_codes` - Manage QR codes
  - `can_edit_absences` - Approve/manage time-off requests
- **Employee Profiles** - Detailed employee information including:
  - Working hours per month
  - Lunch break settings
  - Holiday entitlement (customizable per employee)
  - Notification preferences
- **Bulk Operations** - Efficient management of multiple employees

### ðŸ”² QR Code System
- **Dynamic QR Generation** - Automatic creation of unique QR codes
- **Location Tracking** - Each QR code tied to specific workplace location
- **QR Code Management** - Create, edit, and deactivate QR codes
- **Printable QR Codes** - Generate A4 PDF for printing and mounting
- **Multi-Location Support** - Unlimited QR codes per company

### â° Time Tracking
- **4 Scan Types**:
  - Arrival (PrÃ­chod)
  - Departure (Odchod)
  - Lunch Break Start
  - Lunch Break End
- **GPS Coordinates** - Records exact location of each scan
- **Reverse Geocoding** - Converts GPS to human-readable addresses
- **Smart Button Logic** - Only shows relevant scan options based on last scan
- **Manual & Auto Lunch Breaks** - Flexible break time tracking
- **Night Hours Tracking** - Automatic calculation of work between 22:00-06:00
- **Real-Time Monitoring** - See who's currently at work

### ðŸ“… Absence Management
- **4 Absence Types**:
  - Vacation (Dovolenka)
  - Sick Leave (PN - PrÃ¡ceneschopnosÅ¥)
  - Doctor Visit (LekÃ¡r)
  - Home Office
- **Approval Workflow**:
  - Employees request time off
  - Email notifications to managers/company
  - Approve/reject with email confirmation
  - Direct approval links in emails
- **Conflict Detection** - Warns about scans on vacation days
- **Calendar Integration** - Visual representation of absences

### ðŸ“Š Analytics & Reports

#### Company Analytics
- **Current Period Statistics**:
  - Today's arrivals/departures
  - Weekly scan counts
  - Monthly comparisons
  - Currently in office list
- **Date Range Analysis** - Custom period selection
- **Top QR Codes** - Most used locations
- **Working Hours Breakdown**:
  - Hours with/without breaks
  - Expected vs. actual hours
  - Overtime calculations
  - Night hours
  - Holiday hours
- **Interactive Charts**:
  - Daily arrivals/departures graph
  - Hourly distribution (24h)
  - QR code usage pie chart

#### PDF Reports (Landscape A4)
- **Daily Attendance Table** with:
  - Date, day of week
  - Arrival/departure times
  - Working hours (HH:MM format)
  - Break time (HH:MM format)
  - QR location scanned
  - Smart notes (holidays, issues, vacation types)
- **Summary Statistics**:
  - Total working days
  - Expected hours (based on contract)
  - Total hours with/without breaks
  - Total break time
  - Overtime hours
  - Night hours (22:00-06:00)
  - Holiday hours
  - Average hours per day
  - Vacation/Home office days
  - Days with issues
- **Holiday Detection** - Automatic recognition of national holidays (SK, DE, ES, EN)
- **Unicode Support** - Perfect rendering of Slovak/German/Spanish characters

#### Excel Reports (.xlsx)
- Identical data to PDF reports
- Formatted tables with colors
- Easy to import into other systems
- Sortable and filterable data

### ðŸ“§ Email Notifications

#### Smart Notification System
- **Scan Notifications** - Configurable per company and per manager:
  - Arrival notifications
  - Departure notifications
- **Vacation Notifications**:
  - New request notifications (to managers with can_edit_absences)
  - Approval confirmations (to employee)
  - Cancellation notifications (if cancelled before start date)
  - Different email content for approved/pending/cancelled states
- **Styled HTML Emails** - Professional, branded email templates
- **Action Links** - Direct links to approve/view details
- **Multi-Language Support** - Emails in user's language

### ðŸ” Advanced Filtering & Search
- **Date Range Picker** - Visual calendar selection
- **Multi-Parameter Filters**:
  - By employee name
  - By QR code location
  - By scan type
  - By absence type
  - By work status (at work/not at work)
- **Real-Time Search** - Instant filtering with datalists
- **Sortable Columns** - Click headers to sort (ASC/DESC)
- **Pagination** - Configurable items per page (10/25/50/100)
- **Filter Persistence** - Maintains filters during navigation

### ðŸ” Security & Audit

#### Audit Log System
- **Complete Activity Tracking**:
  - All CRUD operations (Create, Read, Update, Delete)
  - Login/logout events
  - Approval actions
- **Detailed Logging**:
  - Actor (who performed action)
  - Action type
  - Timestamp
  - Message/description
  - IP address
- **Filterable Logs** - Search by actor, action, date range
- **Company/Manager View** - See all company activities
- **User View** - Employees see their own logs

#### Access Control
- **Session-Based Authentication** - Separate sessions for companies and users
- **Permission Checks** - Every action validates permissions
- **Manager Restrictions** - Granular control over what managers can do
- **Automatic Redirects** - Unauthorized users redirected appropriately

### ðŸŒ Internationalization (i18n)
- **4 Languages**:
  - Slovak (SK) - Primary
  - English (EN)
  - German (DE)
  - Spanish (ES)
- **Language Switcher** - Change language on-the-fly
- **Translated Content**:
  - UI elements
  - Email templates
  - PDF reports
  - Error messages
  - Date formats

### ðŸ“± Responsive Design
- **Mobile-First** - Optimized for smartphones
- **Desktop Views** - Full-featured tables and dashboards
- **Tablet Support** - Adaptive layouts
- **Touch-Friendly** - Large buttons and touch targets
- **QR Scanner** - Native camera access on mobile

### ðŸŽ¨ User Interface
- **Modern Design** - Clean, professional Bootstrap 5 interface
- **Color-Coded** - Visual indicators for different states:
  - Blue - Info/Primary actions
  - Green - Success/Approved
  - Orange - Warnings/Sick leave
  - Red - Errors/Urgent
  - Purple - Doctor visits
- **Icons** - Font Awesome icons throughout
- **Dark/Light Elements** - Contrast for readability
- **SweetAlert2** - Beautiful confirmation dialogs
- **Loading States** - Visual feedback for all actions

### ðŸ”„ Additional Features
- **Password Reset** - Email-based password recovery for companies
- **Auto Lunch Breaks** - Optional automatic break deduction
- **Vacation Day Counters** - Track remaining vacation days
- **Holiday Calendar** - Country-specific holiday recognition
- **Home Office Support** - Special absence type for remote work
- **Data Export** - Download reports in PDF/Excel format
- **Whitespace Management** - Clean data handling and validation

## ðŸ› ï¸ Technical Stack

### Backend
- **Django 5.2.9** - Modern Python web framework
- **Python 3.x** - Latest stable version
- **MySQL Connector** - Database connectivity
- **Gunicorn** - Production WSGI server

### Frontend
- **Bootstrap 5** - Responsive CSS framework
- **JavaScript ES6+** - Modern JavaScript
- **Font Awesome** - Icon library
- **SweetAlert2** - Beautiful alerts
- **Daterangepicker** - Advanced date selection

### PDF Generation
- **ReportLab 4.4.7** - Professional PDF creation
- **DejaVu Fonts** - Unicode character support
- **Landscape A4** - Optimized layout

### Excel Generation
- **OpenPyXL 3.1.5** - Excel file creation
- **Styled Cells** - Colors, fonts, borders
- **Formula Support** - Ready for calculations

### Additional Libraries
- **QRCode 8.2** - QR code generation
- **Pillow 12.1** - Image processing
- **Requests 2.32** - HTTP library for geocoding
- **Holidays 0.60** - Holiday calendar support
- **python-dotenv** - Environment variable management

### Deployment
- **Docker Support** - Containerized deployment
- **WhiteNoise** - Static file serving
- **Gunicorn** - Production server
- **MySQL/SQLite** - Database options

## ðŸ“ Project Structure

```
qr_reader/
â”œâ”€â”€ viewer/                      # Main application
â”‚   â”œâ”€â”€ models.py               # Database models
â”‚   â”œâ”€â”€ views.py                # View functions
â”‚   â”œâ”€â”€ admin.py                # Django admin
â”‚   â”œâ”€â”€ templates/              # HTML templates
â”‚   â””â”€â”€ migrations/             # Database migrations
â”œâ”€â”€ qr_reader_django/           # Core modules
â”‚   â”œâ”€â”€ crud.py                 # CRUD operations
â”‚   â”œâ”€â”€ crud_qr_code.py        # QR code operations
â”‚   â”œâ”€â”€ crud_user.py           # User operations
â”‚   â”œâ”€â”€ crud_vacation.py       # Absence operations
â”‚   â”œâ”€â”€ login_register_logout.py # Authentication
â”‚   â”œâ”€â”€ generate_pdf_excel.py  # Report generation
â”‚   â”œâ”€â”€ audit.py               # Audit logging
â”‚   â”œâ”€â”€ settings.py            # Django settings
â”‚   â””â”€â”€ urls.py                # URL routing
â”œâ”€â”€ static/                     # Static files
â”‚   â”œâ”€â”€ css/                   # Stylesheets
â”‚   â”œâ”€â”€ scripts/               # JavaScript
â”‚   â”œâ”€â”€ fontawesome/           # Icons
â”‚   â”œâ”€â”€ fonts/                 # DejaVu fonts
â”‚   â””â”€â”€ images/                # Images
â”œâ”€â”€ media/                      # User uploads
â”‚   â”œâ”€â”€ qr_codes/              # Generated QR codes
â”‚   â””â”€â”€ PDF/                   # Generated reports
â”œâ”€â”€ locale/                     # Translations
â”‚   â”œâ”€â”€ sk/                    # Slovak
â”‚   â”œâ”€â”€ de/                    # German
â”‚   â””â”€â”€ es/                    # Spanish
â”œâ”€â”€ docker-compose.yml         # Docker configuration
â”œâ”€â”€ Dockerfile                 # Docker image
â”œâ”€â”€ requirements.txt           # Python dependencies
â””â”€â”€ manage.py                  # Django management

```

## ðŸš€ Key Use Cases

### Small Businesses (1-50 employees)
- Simple time tracking
- Basic vacation management
- Single location monitoring

### Medium Companies (50-200 employees)
- Multiple locations/departments
- Manager hierarchy
- Detailed analytics
- Compliance reporting

### Large Enterprises (200+ employees)
- Multi-site operations
- Complex approval workflows
- Advanced analytics
- Integration-ready (API can be added)

### Industries
- âœ… Manufacturing
- âœ… Retail
- âœ… Hospitality
- âœ… Construction
- âœ… Healthcare
- âœ… Education
- âœ… Logistics
- âœ… Professional Services

## ðŸ’¡ Business Benefits

1. **Cost Savings**
   - Eliminate manual timesheets
   - Reduce payroll errors
   - Prevent time theft
   - Minimize administrative overhead

2. **Compliance**
   - Accurate time records
   - Audit trails
   - Holiday tracking
   - Work hour regulations

3. **Productivity**
   - Real-time attendance visibility
   - Quick approval processes
   - Mobile accessibility
   - Automated calculations

4. **Insights**
   - Working pattern analysis
   - Overtime monitoring
   - Location utilization
   - Absence trends

5. **Employee Satisfaction**
   - Easy-to-use interface
   - Self-service vacation requests
   - Transparent time tracking
   - Mobile convenience

## ðŸ”’ Security Features

- âœ… Password hashing (Django's built-in)
- âœ… Session management
- âœ… CSRF protection
- âœ… SQL injection prevention
- âœ… XSS protection
- âœ… Secure password reset
- âœ… IP address logging
- âœ… Permission validation
- âœ… Soft deletes (data retention)

## ðŸ“ˆ Scalability

- **Database**: MySQL for production, easily scales
- **Caching**: Ready for Redis/Memcached
- **Load Balancing**: Gunicorn supports multiple workers
- **Docker**: Easy horizontal scaling
- **Media Storage**: Can be moved to S3/Cloud storage
- **API Ready**: RESTful structure allows easy API addition

## ðŸŽ¯ Future Enhancement Possibilities

- Mobile app (React Native/Flutter)
- REST API for integrations
- Biometric authentication
- Facial recognition
- Geofencing
- Shift scheduling
- Payroll integration
- Advanced reporting dashboard
- Real-time notifications (WebSockets)
- Mobile push notifications
- Calendar sync (Google/Outlook)
- Slack/Teams integration

## ðŸ“ž Support

- Professional codebase
- Well-documented
- Modular architecture
- Easy to extend
- Clean separation of concerns

## ðŸ† Why Choose This System?

1. **Complete Solution** - Everything needed out of the box
2. **Modern Technology** - Built with latest tools and best practices
3. **User-Friendly** - Intuitive interface for all user levels
4. **Flexible** - Adapts to different business needs
5. **Reliable** - Robust error handling and validation
6. **Maintainable** - Clean code, easy to update
7. **Multi-Language** - International business ready
8. **Mobile-First** - Works perfectly on any device
9. **Secure** - Enterprise-grade security
10. **Proven** - Production-ready code

## ðŸ’° Value Proposition

This is not just an attendance system - it's a complete workforce management platform that:
- Saves hours of administrative work daily
- Provides accurate data for business decisions
- Ensures compliance with labor regulations
- Scales with your business growth
- Requires minimal training
- Works anywhere, anytime

---

**Ready to modernize your workforce management?** This system delivers everything you need to track, manage, and optimize your team's time and attendance.

