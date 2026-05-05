"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from farm.admin import farm_admin
from farm.react_views import ReactAppView

urlpatterns = [
    path('admin/', farm_admin.urls),
    path('api/', include('farm.api_urls')),
    path('', include('farm.urls')),
    # Serve React app for all remaining routes (SPA fallback)
    re_path(r'^(?!media|static|admin|api).*$', ReactAppView.as_view(), name='react_app'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Enable static files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
