"""
URL configuration for Cloud Task Manager project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Django's set_language view (/i18n/setlang/): persists the chosen
    # language in a cookie.
    path('i18n/', include('django.conf.urls.i18n')),
    # django-allauth: /accounts/google/login/ (+ /callback/) exists only when
    # OAuth credentials are configured; the other account URLs stay inert.
    path('accounts/', include('allauth.urls')),
    path('', include('tasks.urls')),
]
