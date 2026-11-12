"""Template context processors for the tasks app."""
from django.conf import settings


def google_oauth(request):
    """Expose whether Google OAuth is configured (credentials come from env).

    Templates use this flag to render the "Continue with Google" button only
    when the Google provider has OAuth credentials; without credentials the
    pages degrade gracefully to username/password authentication only.
    """
    providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
    return {'google_oauth_enabled': bool(providers.get('google', {}).get('APPS'))}
