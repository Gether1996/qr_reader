# Setup script for QR Reader System
# This script will help you set up and run the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QR Reader System - Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host ""

# Create a backup of the old database
if (Test-Path "db.sqlite3") {
    Write-Host "Backing up old database..." -ForegroundColor Yellow
    Copy-Item "db.sqlite3" "db.sqlite3.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "Backup created!" -ForegroundColor Green
    Write-Host ""
    
    $response = Read-Host "Do you want to delete the old database and start fresh? (y/n)"
    if ($response -eq 'y') {
        Remove-Item "db.sqlite3"
        Write-Host "Old database deleted." -ForegroundColor Yellow
    }
}

Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate

Write-Host ""
Write-Host "Migrations completed!" -ForegroundColor Green
Write-Host ""

# Ask to create superuser
$createSuper = Read-Host "Do you want to create a Django admin superuser? (y/n)"
if ($createSuper -eq 'y') {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the development server, run:" -ForegroundColor Yellow
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Then visit:" -ForegroundColor Yellow
Write-Host "  http://localhost:8000 - Main application" -ForegroundColor White
Write-Host "  http://localhost:8000/admin - Admin panel" -ForegroundColor White
Write-Host ""
