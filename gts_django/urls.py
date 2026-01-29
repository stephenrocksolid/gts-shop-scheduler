"""
URL configuration for gts_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
import os
from rental_scheduler.error_views import handler400, handler403, handler404, handler500


def license_serve(request, path):
    """Serve license files from the media directory"""
    return serve(request, path, document_root=os.path.join(settings.MEDIA_ROOT, 'licenses'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rental_scheduler.urls')),  # Include rental_scheduler URLs at root
    path('licenses/<path:path>', license_serve),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()

# Register error handlers
handler400 = 'rental_scheduler.error_views.handler400'  # Bad request
handler403 = 'rental_scheduler.error_views.handler403'  # Permission denied
handler404 = 'rental_scheduler.error_views.handler404'  # Not found
handler500 = 'rental_scheduler.error_views.handler500'  # Server error
