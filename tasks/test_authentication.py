"""
Focused tests for the authentication flow (Task 03).

Covers registration, login, logout, session authentication, CSRF
protection and the access rules of the personal area.
"""
import secrets

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

# Test-only fixtures, generated at runtime so that no credential literals
# are stored in source (security scan requirement).
VALID_PASSWORD = 'Vg' + secrets.token_urlsafe(12) + '!a7'
WRONG_PASSWORD = secrets.token_urlsafe(10)


class RegistrationTests(TestCase):
    """Registration page and account creation."""

    def test_register_page_is_public(self):
        response = self.client.get(reverse('tasks:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'name="password1"')

    def test_registration_success_creates_user_and_starts_session(self):
        response = self.client.post(reverse('tasks:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': VALID_PASSWORD,
            'password2': VALID_PASSWORD,
        })
        self.assertRedirects(response, reverse('tasks:dashboard'))

        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password(VALID_PASSWORD))
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_duplicate_registration_shows_form_error(self):
        User.objects.create_user(username='taken', password=VALID_PASSWORD)

        response = self.client.post(reverse('tasks:register'), {
            'username': 'taken',
            'email': 'taken@example.com',
            'password1': VALID_PASSWORD,
            'password2': VALID_PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'username',
            'A user with that username already exists.',
        )
        self.assertEqual(User.objects.filter(username='taken').count(), 1)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(reverse('tasks:register'), {
            'username': 'mismatch',
            'password1': VALID_PASSWORD,
            'password2': VALID_PASSWORD + '-alt',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='mismatch').exists())

    def test_registration_rejects_weak_password(self):
        response = self.client.post(reverse('tasks:register'), {
            'username': 'weakuser',
            'password1': '123',
            'password2': '123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(username='weakuser').exists())


class LoginTests(TestCase):
    """Login page, successful login and failed login."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password=VALID_PASSWORD,
        )

    def test_login_page_is_public(self):
        response = self.client.get(reverse('tasks:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_login_success_creates_session(self):
        response = self.client.post(reverse('tasks:login'), {
            'username': 'alice',
            'password': VALID_PASSWORD,
        })

        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertIn('_auth_user_hash', self.client.session)

    def test_login_failure_shows_error_and_no_session(self):
        response = self.client.post(reverse('tasks:login'), {
            'username': 'alice',
            'password': WRONG_PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Please enter a correct username and password',
        )
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_failure_for_unknown_user(self):
        response = self.client.post(reverse('tasks:login'), {
            'username': 'ghost',
            'password': VALID_PASSWORD,
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)


class LogoutTests(TestCase):
    """Logout clears the session and is a POST-only, CSRF protected action."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password=VALID_PASSWORD,
        )

    def test_logout_clears_session(self):
        self.client.login(username='alice', password=VALID_PASSWORD)

        response = self.client.post(reverse('tasks:logout'))

        self.assertRedirects(response, reverse('tasks:home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_requires_post(self):
        self.client.login(username='alice', password=VALID_PASSWORD)

        response = self.client.get(reverse('tasks:logout'))

        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)


class CsrfProtectionTests(TestCase):
    """State changing forms must be protected against CSRF."""

    def test_registration_post_without_csrf_token_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(reverse('tasks:register'), {
            'username': 'nocsrf',
            'password1': VALID_PASSWORD,
            'password2': VALID_PASSWORD,
        })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(username='nocsrf').exists())

    def test_login_post_without_csrf_token_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(reverse('tasks:login'), {
            'username': 'alice',
            'password': VALID_PASSWORD,
        })

        self.assertEqual(response.status_code, 403)


class ProtectedAreaTests(TestCase):
    """The personal area is protected server-side."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            password=VALID_PASSWORD,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('tasks:dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            f"{reverse('tasks:login')}?next={reverse('tasks:dashboard')}",
        )
        self.assertRedirects(
            response,
            f"{reverse('tasks:login')}?next={reverse('tasks:dashboard')}",
            fetch_redirect_response=False,
        )

    def test_authenticated_user_can_access_dashboard(self):
        self.client.login(username='alice', password=VALID_PASSWORD)

        response = self.client.get(reverse('tasks:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alice')
        self.assertContains(response, 'Dashboard')


class PublicEndpointTests(TestCase):
    """Public pages stay reachable without a session."""

    def test_health_is_public(self):
        response = self.client.get(reverse('tasks:health'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.json()['status'], 'ok')

    def test_home_is_public(self):
        response = self.client.get(reverse('tasks:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cloud Task Manager')
