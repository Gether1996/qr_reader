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
    list_display = ('qr_code', 'scanned_by', 'latitude', 'longitude', 'timestamp')
    list_filter = ('timestamp', 'qr_code__company')
    search_fields = ('qr_code__name', 'scanned_by__name')
    readonly_fields = ('timestamp',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('qr_code', 'scanned_by')
