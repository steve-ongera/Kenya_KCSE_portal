from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kcse_portal.urls')),  # Main application URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Additional auth URLs
]

