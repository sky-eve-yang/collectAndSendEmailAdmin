"""collectAndSendEmailAdmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(url='/admin/')),
    path("admin/", admin.site.urls),
    path("graduate_add/", views.graduate_add, name="graduate_add"),
    path("change_audit_status/", views.change_audit_status, name="change_audit_status"),
    path("handle_send_email/", views.handle_send_email, name="handle_send_email"),
    path("generate_word/", views.generate_word, name="generate_word"),
    path("upload/", views.file_upload_view, name="file_upload"),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)