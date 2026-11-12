"""
Focused tests for Google Sign-In (django-allauth).

Two modes:
- Unconfigured (no OAuth credentials in the environment): the Google button
  must not appear and the provider routes must not resolve, while regular
  username/password authentication keeps working.
- Configured (GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET set, dummy
  runtime-generated values for tests): the button appears on login/signup
  and the Google provider routes resolve.

The safe-linking guards (no automatic account takeover by matching email)
are asserted in both modes.
"""
import os
import secrets
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

# Test-only fixtures, generated at runtime so that no credential literals
# are stored in source (security scan requirement).
VALID_PASSWORD = 'Vg' + secrets.token_urlsafe(12) + '!a7'

GOOGLE_ENABLED = getattr(settings, 'GOOGLE_OAUTH_ENABLED', False)
GOOGLE_LOGIN_PATH = '/accounts/google/login/'


class SafeLinkingGuardTests(TestCase):
    """Email-matching auto-login / auto-link must be disabled in every mode."""

    def test_email_based_linking_is_disabled(self):
        from allauth.socialaccount import app_settings

        self.assertFalse(app_settings.EMAIL_AUTHENTICATION)
        self.assertFalse(app_settings.EMAIL_AUTHENTICATION_AUTO_CONNECT)
        self.assertFalse(settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION)
        self.assertFalse(settings.SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT)

    def test_existing_email_account_is_not_taken_over_by_default(self):
        """A Google login carrying an existing email must not match by email."""
        User.objects.create_user(
            username='owner', email='owner@example.com', password=VALID_PASSWORD,
        )
        from allauth.socialaccount.adapter import get_adapter
        from allauth.socialaccount.models import SocialAccount, SocialApp, SocialLogin
        from allauth.socialaccount.providers.google.provider import GoogleProvider

        app = SocialApp(provider='google', client_id=secrets.token_urlsafe(12))
        provider = GoogleProvider(None, app=app)
        sociallogin = SocialLogin(
            provider=provider,
            account=SocialAccount(provider='google', uid='attacker-uid'),
        )
        adapter = get_adapter()
        # With the guards off, email-based authentication of the existing
        # account is refused and the flow falls back to the explicit
        # social-signup form.
        self.assertFalse(adapter.can_authenticate_by_email(sociallogin, 'owner@example.com'))


class GoogleOAuthDisabledTests(TestCase):
    """Without credentials, pages degrade to username/password only."""

    @override_settings(SOCIALACCOUNT_PROVIDERS={})
    def test_login_page_has_no_google_button(self):
        response = self.client.get(reverse('tasks:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertNotContains(response, 'Continue with Google')

    @override_settings(SOCIALACCOUNT_PROVIDERS={})
    def test_signup_page_has_no_google_button(self):
        response = self.client.get(reverse('tasks:register'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Continue with Google')

    @skipUnless(not GOOGLE_ENABLED, 'Google OAuth credentials are configured')
    def test_google_provider_routes_do_not_resolve(self):
        response = self.client.get(GOOGLE_LOGIN_PATH)
        self.assertEqual(response.status_code, 404)

    def test_username_password_login_still_works(self):
        User.objects.create_user(username='alice', password=VALID_PASSWORD)
        response = self.client.post(reverse('tasks:login'), {
            'username': 'alice', 'password': VALID_PASSWORD,
        })
        self.assertRedirects(response, reverse('tasks:dashboard'))
        user = User.objects.get(username='alice')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)


@skipUnless(GOOGLE_ENABLED, 'Google OAuth credentials are not configured')
class GoogleOAuthEnabledTests(TestCase):
    """With credentials configured through environment variables."""

    def test_credentials_come_from_environment(self):
        app = settings.SOCIALACCOUNT_PROVIDERS['google']['APPS'][0]
        self.assertEqual(app['client_id'], os.environ['GOOGLE_OAUTH_CLIENT_ID'])
        self.assertEqual(app['secret'], os.environ['GOOGLE_OAUTH_CLIENT_SECRET'])

    def test_login_page_shows_google_button(self):
        response = self.client.get(reverse('tasks:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, GOOGLE_LOGIN_PATH)

    def test_signup_page_shows_google_button(self):
        response = self.client.get(reverse('tasks:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Continue with Google')
        self.assertContains(response, GOOGLE_LOGIN_PATH)

    def test_google_login_initiates_redirect_to_google(self):
        response = self.client.post(GOOGLE_LOGIN_PATH)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith('https://accounts.google.com/o/oauth2/'),
            f'Unexpected redirect target: {response.url}',
        )
        self.assertIn('client_id=', response.url)

    def test_google_callback_route_is_registered(self):
        self.assertEqual(reverse('google_callback'), GOOGLE_LOGIN_PATH + 'callback/')
