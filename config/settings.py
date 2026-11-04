"""
Django settings for Cloud Task Manager project.
"""

import os
from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _


def _required_env(name):
    """Return a required, non-blank environment value.

    The value itself is never logged or echoed; only the variable name appears
    in the error message.
    """
    value = config(name, default='')
    if not isinstance(value, str) or not value.strip():
        raise ImproperlyConfigured(
            f"{name} environment variable is required and must not be blank."
        )
    return value


# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = _required_env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Explicit runtime environment separation. 'local' serves plain HTTP on
# 127.0.0.1; 'production' serves HTTPS terminated by the reverse proxy.
ENVIRONMENT = config('DJANGO_ENV', default='production').strip().lower()

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tasks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # Guarantees the Vietnamese default for first-time visitors (no explicit
    # choice yet) by neutralizing the browser Accept-Language header before
    # LocaleMiddleware negotiates the active language.
    'config.middleware.default_language_middleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Required: format postgresql://user:password@host:port/dbname
DATABASE_URL = _required_env('DATABASE_URL')

# Parse DATABASE_URL
import dj_database_url
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# Vietnamese is the default UI language; English is available as an option.
# The active language is stored in a cookie by Django's set_language view, so
# an explicit choice persists across navigation and login/logout.
LANGUAGE_CODE = 'vi'
LANGUAGES = [
    ('vi', _('Vietnamese')),
    ('en', _('English')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Django 5.1 removed STATICFILES_STORAGE / DEFAULT_FILE_STORAGE in favour of
# the STORAGES mapping. Keep the default FileSystemStorage backend and use
# WhiteNoise for compressed, manifest-hashed static files.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings.
# Defaults are production-safe (HTTPS enforced). The local stack explicitly
# sets DJANGO_ENV=local in docker-compose.yml to serve plain HTTP on 127.0.0.1
# without a TLS listener. DEBUG is NOT used to relax these settings.
if not DEBUG:
    _prod = ENVIRONMENT == 'production'
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=_prod, cast=bool)
    # Container/host health probes poll /health/ over plain HTTP; keep that
    # single endpoint reachable without a TLS listener in every environment.
    SECURE_REDIRECT_EXEMPT = [r'^health/?$']
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=_prod, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=_prod, cast=bool)
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# Login URLs
LOGIN_URL = '/login/'
# Successful login lands on the personal area, logout returns to the login page.
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
