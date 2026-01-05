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
    path('company/settings/', views.company_settings, name='company_settings'),
    path('company/request-password-reset/', views.company_request_password_reset, name='company_request_password_reset'),
    path('company/reset-password/<str:token>/', views.company_reset_password, name='company_reset_password'),
    
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
    path('company/user/<int:user_id>/attendance-excel/', views.generate_attendance_excel, name='generate_attendance_excel'),
    
    # Vacation management (company actions)
    path('absence/create/', views.create_vacation, name='create_vacation'),
    path('absence/<int:vacation_id>/edit/', views.edit_vacation, name='edit_vacation'),
    path('absence/<int:vacation_id>/delete/', views.delete_vacation, name='delete_vacation'),
    path('absence/<int:vacation_id>/approve/', views.approve_vacation, name='approve_vacation'),
    
    # Analytics
    path('company/analytics/', views.company_analytics, name='company_analytics'),
    path('api/analytics/chart-data/', views.analytics_chart_data, name='analytics_chart_data'),
    
    # Audit logging
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    
    # Magazine routes
    path('magazine/', views.magazine_dashboard, name='magazine_dashboard'),
    path('magazine/editor/', views.magazine_editor, name='magazine_editor'),
    path('magazine/editor/<int:magazine_id>/', views.magazine_editor, name='magazine_editor'),
    path('magazine/<int:magazine_id>/preview/', views.magazine_preview, name='magazine_preview'),
    
    # Magazine API endpoints
    path('magazine/<int:magazine_id>/update/', views.api_magazine_update, name='api_magazine_update'),
    path('magazine/<int:magazine_id>/delete/', views.api_magazine_delete, name='api_magazine_delete'),
    path('magazine/<int:magazine_id>/article/create/', views.api_article_create, name='api_article_create'),
    path('magazine/article/<int:article_id>/data/', views.api_article_data, name='api_article_data'),
    path('magazine/article/<int:article_id>/update/', views.api_article_update, name='api_article_update'),
    path('magazine/article/<int:article_id>/delete/', views.api_article_delete, name='api_article_delete'),
    path('magazine/article/<int:article_id>/upload-header-image/', views.api_article_upload_header_image, name='api_article_upload_header_image'),
    path('magazine/article/<int:article_id>/remove-header-image/', views.api_article_remove_header_image, name='api_article_remove_header_image'),
    path('magazine/article/<int:article_id>/block/create/', views.api_content_block_create, name='api_content_block_create'),
    path('magazine/article/<int:article_id>/reorder-blocks/', views.api_article_reorder_blocks, name='api_article_reorder_blocks'),
    path('magazine/block/<int:block_id>/update/', views.api_content_block_update, name='api_content_block_update'),
    path('magazine/block/<int:block_id>/delete/', views.api_content_block_delete, name='api_content_block_delete'),
    
    path('admin/', admin.site.urls),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
