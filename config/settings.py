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
    # django-allauth: session-based authentication support for Google sign-in.
    # The core apps are always installed so the "Continue with Google" button
    # gate and the /accounts/ URLs behave consistently in every environment;
    # the Google provider itself is only registered when OAuth credentials
    # are present (see GOOGLE_OAUTH_ENABLED below).
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
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
    # Required by django-allauth (raises ImproperlyConfigured otherwise).
    # Must come after AuthenticationMiddleware.
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Authentication backends. The ModelBackend keeps the existing
# username/password flow (and its task ownership) untouched; allauth's
# backend only authenticates through the social login flow.
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
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
                'tasks.context_processors.google_oauth',
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
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
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
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG else 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        ),
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

# django-allauth configuration.
# Credentials are provided exclusively through environment variables; they
# are never written to source code, fixtures or documentation.
_GOOGLE_CLIENT_ID = config('GOOGLE_OAUTH_CLIENT_ID', default='')
_GOOGLE_CLIENT_SECRET = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')
GOOGLE_OAUTH_ENABLED = bool(_GOOGLE_CLIENT_ID.strip() and _GOOGLE_CLIENT_SECRET.strip())

# Account behaviour. Username/password login and signup keep working exactly
# as before (they still run through the ModelBackend and the tasks app
# views); allauth only adds the Google social login path.
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# Safe-linking guards. By default django-allauth never logs an existing user
# in just because a social account carries the same email address. Both
# settings are pinned explicitly here so that a future dependency or
# deployment change cannot silently re-enable matching-by-email, which would
# let anyone with a Google account of an email address take over an existing
# workspace. Instead, Google sign-in with an unknown (provider, email) pair
# always goes through the explicit social-signup confirmation form.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = False
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = False
# Do not pre-fill/login existing users by email, and do not auto-link.
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_STORE_TOKENS = True

if GOOGLE_OAUTH_ENABLED:
    INSTALLED_APPS.append('allauth.socialaccount.providers.google')
    # Settings-based app configuration: no SocialApp database rows are
    # required, so no data migration is needed for Google sign-in.
    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'APPS': [
                {
                    'client_id': _GOOGLE_CLIENT_ID,
                    'secret': _GOOGLE_CLIENT_SECRET,
                },
            ],
        },
    }

# Login URLs
LOGIN_URL = '/login/'
# Successful login lands on the personal area, logout returns to the login page.
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
