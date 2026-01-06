from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from viewer import views
from qr_reader_django.generate_pdf_excel import generate_qr_code_pdf, generate_attendance_pdf, generate_attendance_excel
from qr_reader_django.general import check_email
from qr_reader_django.login_register_logout import company_register, company_login, company_logout, user_login, user_logout
from qr_reader_django.crud_qr_code import create_qr_code, delete_qr_code
from qr_reader_django.crud_user import create_user, delete_user, edit_user
from qr_reader_django.crud_vacation import create_vacation, edit_vacation, delete_vacation, approve_vacation
from qr_reader_django.magazine import magazine_dashboard, magazine_editor, magazine_preview, api_magazine_update, api_magazine_delete, api_article_create, api_article_data, api_article_update, api_article_delete, api_article_upload_header_image, api_article_remove_header_image, api_content_block_create, api_article_reorder_blocks, api_content_block_update, api_content_block_delete

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns.append(re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}))

urlpatterns += i18n_patterns(
    # Landing page
    path('', views.landing_page, name='landing_page'),
    
    # Company routes
    path('company/register/', company_register, name='company_register'),
    path('company/login/', company_login, name='company_login'),
    path('company/logout/', company_logout, name='company_logout'),
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/settings/', views.company_settings, name='company_settings'),
    path('company/request-password-reset/', views.company_request_password_reset, name='company_request_password_reset'),
    path('company/reset-password/<str:token>/', views.company_reset_password, name='company_reset_password'),
    
    # User routes
    path('user/login/', user_login, name='user_login'),
    path('user/logout/', user_logout, name='user_logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/scan/', views.user_scan_qr, name='user_scan_qr'),
    
    # QR Code management (company actions)
    path('qr/create/', create_qr_code, name='create_qr_code'),
    path('qr/delete/<int:qr_id>/', delete_qr_code, name='delete_qr_code'),
    path('qr/scans/<int:qr_id>/', views.view_qr_scans, name='view_qr_scans'),
    path('qr/<int:qr_id>/pdf/', generate_qr_code_pdf, name='generate_qr_code_pdf'),
    
    # User management (company actions)
    path('user/check-email/', check_email, name='check_email'),
    path('user/create/', create_user, name='create_user'),
    path('company/user/<int:user_id>/edit/', edit_user, name='edit_user'),
    path('company/user/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('company/user/<int:user_id>/details/', views.view_user_details, name='view_user_details'),
    path('company/user/<int:user_id>/attendance-pdf/', generate_attendance_pdf, name='generate_attendance_pdf'),
    path('company/user/<int:user_id>/attendance-excel/', generate_attendance_excel, name='generate_attendance_excel'),
    
    # Vacation management (company actions)
    path('absence/create/', create_vacation, name='create_vacation'),
    path('absence/<int:vacation_id>/edit/', edit_vacation, name='edit_vacation'),
    path('absence/<int:vacation_id>/delete/', delete_vacation, name='delete_vacation'),
    path('absence/<int:vacation_id>/approve/', approve_vacation, name='approve_vacation'),
    
    # Analytics
    path('company/analytics/', views.company_analytics, name='company_analytics'),
    path('api/analytics/chart-data/', views.analytics_chart_data, name='analytics_chart_data'),
    
    # Audit logging
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    
    # Magazine routes
    path('magazine/', magazine_dashboard, name='magazine_dashboard'),
    path('magazine/editor/', magazine_editor, name='magazine_editor'),
    path('magazine/editor/<int:magazine_id>/', magazine_editor, name='magazine_editor'),
    path('magazine/<int:magazine_id>/preview/', magazine_preview, name='magazine_preview'),
    
    # Magazine API endpoints
    path('magazine/<int:magazine_id>/update/', api_magazine_update, name='api_magazine_update'),
    path('magazine/<int:magazine_id>/delete/', api_magazine_delete, name='api_magazine_delete'),
    path('magazine/<int:magazine_id>/article/create/', api_article_create, name='api_article_create'),
    path('magazine/article/<int:article_id>/data/', api_article_data, name='api_article_data'),
    path('magazine/article/<int:article_id>/update/', api_article_update, name='api_article_update'),
    path('magazine/article/<int:article_id>/delete/', api_article_delete, name='api_article_delete'),
    path('magazine/article/<int:article_id>/upload-header-image/', api_article_upload_header_image, name='api_article_upload_header_image'),
    path('magazine/article/<int:article_id>/remove-header-image/', api_article_remove_header_image, name='api_article_remove_header_image'),
    path('magazine/article/<int:article_id>/block/create/', api_content_block_create, name='api_content_block_create'),
    path('magazine/article/<int:article_id>/reorder-blocks/', api_article_reorder_blocks, name='api_article_reorder_blocks'),
    path('magazine/block/<int:block_id>/update/', api_content_block_update, name='api_content_block_update'),
    path('magazine/block/<int:block_id>/delete/', api_content_block_delete, name='api_content_block_delete'),
    
    path('admin/', admin.site.urls),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
