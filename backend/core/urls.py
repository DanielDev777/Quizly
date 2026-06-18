"""
URL configuration for core project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.static import serve
import os

FRONTEND_DIR = os.path.join(settings.BASE_DIR.parent, 'frontend')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('quiz.api.urls')),
    # Serve frontend files so frontend + API share the same origin (port 8000)
    re_path(r'^(?P<path>.*)$', serve, {'document_root': FRONTEND_DIR, 'show_indexes': True}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
