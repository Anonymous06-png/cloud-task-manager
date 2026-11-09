"""
Foundation smoke tests for Cloud Task Manager.
"""
import os
import re
import secrets
import subprocess
import sys

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, SimpleTestCase, Client, override_settings
from django.urls import reverse
from django.utils.translation import gettext, override
from .models import Task

# Test-only fixtures, generated at runtime so that no credential literals
# are stored in source (security scan requirement).
FIXTURE_PASSWORD = secrets.token_urlsafe(16) + '!a7'
SUBPROCESS_TEST_SECRET_KEY = secrets.token_urlsafe(32)


class FoundationSmokeTests(TestCase):
    """Basic smoke tests for Django foundation."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password=FIXTURE_PASSWORD
        )

    def test_home_page_loads(self):
        """Test that home page returns 200."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cloud Task Manager')

    def test_health_check_endpoint(self):
        """Test health check returns valid JSON."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertIn('version', data)

    def test_task_model_creation(self):
        """Test Task model can be created."""
        task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='Test description',
            status='pending'
        )
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.user, self.user)

    def test_task_model_str(self):
        """Test Task model string representation."""
        task = Task.objects.create(
            user=self.user,
            title='Sample Task',
            status='completed'
        )
        for language in ('vi', 'en'):
            with self.subTest(language=language), override(language):
                expected = f"Sample Task ({gettext('Completed')})"
                self.assertEqual(str(task), expected)


class ConfigurationTests(SimpleTestCase):
    """Focused checks for the settings corrected in Task 02C."""

    def test_staticfiles_storage_uses_whitenoise(self):
        self.assertEqual(
            settings.STORAGES['staticfiles']['BACKEND'],
            'whitenoise.storage.CompressedManifestStaticFilesStorage',
        )

    def test_default_file_storage_is_filesystem(self):
        self.assertEqual(
            settings.STORAGES['default']['BACKEND'],
            'django.core.files.storage.FileSystemStorage',
        )

    def test_removed_staticfiles_storage_setting_absent(self):
        self.assertNotIn('STATICFILES_STORAGE', dir(settings))
        self.assertNotIn('DEFAULT_FILE_STORAGE', dir(settings))

    def test_health_route_resolves_to_health_slash(self):
        self.assertEqual(reverse('tasks:health'), '/health/')

    def test_health_is_exempt_from_ssl_redirect(self):
        patterns = settings.SECURE_REDIRECT_EXEMPT
        self.assertTrue(any(re.search(p, 'health/') for p in patterns))


class HealthRedirectTests(SimpleTestCase):
    """The health endpoint must stay reachable without a TLS listener."""

    @override_settings(
        DEBUG=False,
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[r'^health/?$'],
    )
    def test_health_not_redirected_when_ssl_redirect_enabled(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)

    @override_settings(
        DEBUG=False,
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[r'^health/?$'],
    )
    def test_other_path_redirected_when_ssl_redirect_enabled(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 301)


class RequiredEnvTests(SimpleTestCase):
    """Missing/blank required secrets must fail fast (values never printed)."""

    def _import_settings(self, **env):
        environment = {**os.environ, **env}
        return subprocess.run(
            [sys.executable, '-c', 'import config.settings'],
            cwd=str(settings.BASE_DIR),
            env=environment,
            capture_output=True,
            text=True,
        )

    def test_blank_secret_key_is_rejected(self):
        result = self._import_settings(SECRET_KEY='   ')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SECRET_KEY', result.stderr)

    def test_blank_database_url_is_rejected(self):
        result = self._import_settings(
            SECRET_KEY=SUBPROCESS_TEST_SECRET_KEY,
            DATABASE_URL='   ',
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('DATABASE_URL', result.stderr)

    def test_valid_required_env_imports(self):
        result = self._import_settings(
            SECRET_KEY=SUBPROCESS_TEST_SECRET_KEY,
            DATABASE_URL='postgresql://user:pass@localhost:5432/db',
            DJANGO_ENV='local',
        )
        self.assertEqual(result.returncode, 0, result.stderr)
