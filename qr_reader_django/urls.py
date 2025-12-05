from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from viewer import views

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Static files served by WhiteNoise in production
if settings.DEBUG:
    urlpatterns.append(re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}))

urlpatterns += i18n_patterns(
    # Landing page
    path('', views.landing_page, name='landing_page'),
    
    # Company routes
    path('company/register/', views.company_register, name='company_register'),
    path('company/login/', views.company_login, name='company_login'),
    path('company/logout/', views.company_logout, name='company_logout'),
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    
    # User routes
    path('user/login/', views.user_login, name='user_login'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/scan/', views.user_scan_qr, name='user_scan_qr'),
    
    # QR Code management (company actions)
    path('qr/create/', views.create_qr_code, name='create_qr_code'),
    path('qr/delete/<int:qr_id>/', views.delete_qr_code, name='delete_qr_code'),
    path('qr/scans/<int:qr_id>/', views.view_qr_scans, name='view_qr_scans'),
    path('qr/<int:qr_id>/pdf/', views.generate_qr_code_pdf, name='generate_qr_code_pdf'),
    
    # User management (company actions)
    path('user/create/', views.create_user, name='create_user'),
    path('company/user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('company/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('company/user/<int:user_id>/details/', views.view_user_details, name='view_user_details'),
    path('company/user/<int:user_id>/attendance-pdf/', views.generate_attendance_pdf, name='generate_attendance_pdf'),
    
    # Vacation management (company actions)
    path('absence/create/', views.create_vacation, name='create_vacation'),
    path('absence/<int:vacation_id>/edit/', views.edit_vacation, name='edit_vacation'),
    
    # Analytics
    path('company/analytics/', views.company_analytics, name='company_analytics'),
    path('api/analytics/chart-data/', views.analytics_chart_data, name='analytics_chart_data'),
    path('absence/<int:vacation_id>/delete/', views.delete_vacation, name='delete_vacation'),
    
    path('admin/', admin.site.urls),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
