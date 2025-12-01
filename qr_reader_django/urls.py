from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from viewer import views

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

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
    
    # QR Code management (company actions)
    path('qr/create/', views.create_qr_code, name='create_qr_code'),
    path('qr/delete/<int:qr_id>/', views.delete_qr_code, name='delete_qr_code'),
    path('qr/scans/<int:qr_id>/', views.view_qr_scans, name='view_qr_scans'),
    
    # User management (company actions)
    path('user/create/', views.create_user, name='create_user'),
    
    # Public scan endpoint
    path('scan/<str:uuid>/', views.scan_qr, name='scan_qr'),
    
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
