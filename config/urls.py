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
    path('', include('tasks.urls')),
]
