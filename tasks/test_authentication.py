"""
Focused tests for the authentication flow (Task 03).

Covers registration, login, logout, session authentication, CSRF
protection and the access rules of the personal area.
"""
import secrets

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils.translation import gettext as _
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
            _('A user with that username already exists.'),
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
        self.assertTrue(response.context['form'].non_field_errors())
        self.assertEqual(
            response.context['form'].errors.as_data()['__all__'][0].code,
            'invalid_login',
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

        self.assertRedirects(response, reverse('tasks:login'))
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
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, _('Overview'))


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
        self.assertTemplateUsed(response, 'home.html')
        self.assertTemplateUsed(response, 'includes/workspace_preview.html')
        self.assertContains(response, _('Make room for the work that matters.'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertNotContains(response, 'class="tech-stack"')
        for name in ('login', 'register'):
            url = reverse(f'tasks:{name}')
            self.assertContains(response, f'href="{url}"')
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_authenticated_entry_pages_redirect_to_dashboard(self):
        user = User.objects.create_user(username='entry-user', password=VALID_PASSWORD)
        self.client.force_login(user)
        for name in ('home', 'login', 'register'):
            with self.subTest(page=name):
                response = self.client.get(reverse(f'tasks:{name}'), follow=True)
                self.assertEqual(response.redirect_chain, [('/dashboard/', 302)])
                self.assertTemplateUsed(response, 'dashboard.html')

    def test_login_logout_entry_journey(self):
        user = User.objects.create_user(username='journey-user', password=VALID_PASSWORD)
        self.assertEqual(self.client.get('/').status_code, 200)
        response = self.client.post('/login/', {
            'username': user.username, 'password': VALID_PASSWORD,
        }, follow=True)
        self.assertEqual(response.redirect_chain, [('/dashboard/', 302)])
        self.assertTemplateUsed(response, 'dashboard.html')
        response = self.client.post('/logout/', follow=True)
        self.assertEqual(response.redirect_chain, [('/login/', 302)])
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'includes/workspace_preview.html')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(self.client.get('/dashboard/'), '/login/?next=/dashboard/')
        self.assertTemplateUsed(self.client.get('/'), 'home.html')

    def test_protected_task_routes_still_require_login(self):
        routes = [
            ('task_list', ()), ('task_create', ()), ('task_detail', (1,)),
            ('task_update', (1,)), ('task_delete', (1,)), ('task_toggle', (1,)),
        ]
        for name, args in routes:
            with self.subTest(page=name):
                url = reverse(f'tasks:{name}', args=args)
                response = self.client.post(url) if name == 'task_toggle' else self.client.get(url)
                self.assertRedirects(response, f'/login/?next={url}')

    def test_logout_without_csrf_keeps_session(self):
        user = User.objects.create_user(username='csrf-user', password=VALID_PASSWORD)
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        response = client.post('/logout/')
        self.assertEqual(response.status_code, 403)
        self.assertIn('_auth_user_id', client.session)

    def test_login_rejects_external_next(self):
        user = User.objects.create_user(username='redirect-user', password=VALID_PASSWORD)
        response = self.client.post('/login/', {
            'username': user.username, 'password': VALID_PASSWORD,
            'next': 'https://untrusted.example/other/',
        })
        self.assertRedirects(response, '/dashboard/')
