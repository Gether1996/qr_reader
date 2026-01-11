from django.contrib import admin
from .models import Company, User, QRCodeProfile, ScanEvent


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'company')
    search_fields = ('name', 'email', 'company__name')
    readonly_fields = ('created_at',)


@admin.register(QRCodeProfile)
class QRCodeProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'location', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at', 'company')
    search_fields = ('name', 'location', 'uuid', 'company__name')
    readonly_fields = ('uuid', 'created_at', 'qr_code')


@admin.register(ScanEvent)
class ScanEventAdmin(admin.ModelAdmin):
    list_display = ('get_scan_location', 'scanned_by', 'scan_type', 'is_home_office', 'is_business_trip', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp', 'scan_type', 'is_home_office', 'is_business_trip', 'qr_code__company')
    search_fields = ('qr_code__name', 'scanned_by__name')
    readonly_fields = ('timestamp',)
    
    def get_scan_location(self, obj):
        """Display scan location - either QR code name, Home Office or Business Trip"""
        if obj.is_home_office:
            return "🏠 Home Office"
        if obj.is_business_trip:
            return "💼 Business Trip"
        return obj.qr_code.name if obj.qr_code else "Unknown"
    get_scan_location.short_description = 'Location'
    get_scan_location.admin_order_field = 'qr_code__name'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('qr_code', 'scanned_by')
