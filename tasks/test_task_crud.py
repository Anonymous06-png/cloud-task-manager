"""
Focused tests for task CRUD (Task 04).

Covers create, read-by-owner-only, update, delete, status filtering,
ownership enforcement against manual URL/ID changes, anonymous redirect,
and invalid form handling without crashes.
"""
import secrets

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import Task

# Test-only fixture, generated at runtime so that no credential literal
# is stored in source (security scan requirement).
VALID_PASSWORD = 'Vg' + secrets.token_urlsafe(12) + '!a7'


def _make_user(username):
    return User.objects.create_user(username=username, password=VALID_PASSWORD)


def _make_task(user, title='Task', status='pending'):
    return Task.objects.create(
        user=user,
        title=title,
        description='description',
        status=status,
    )


class TaskSetupMixin:
    """Shared fixtures for task tests."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user('alice')
        self.other_user = _make_user('bob')
        self.client.login(username='alice', password=VALID_PASSWORD)


class TaskCrudTests(TaskSetupMixin, TestCase):
    """Owned create / read / update / delete for the signed-in user."""

    def test_create_task(self):
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'New task',
            'description': 'Details',
            'status': 'pending',
        })
        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertTrue(
            Task.objects.filter(user=self.user, title='New task').exists()
        )

    def test_create_task_with_due_date(self):
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'Due task',
            'due_date': '2027-01-01',
            'status': 'pending',
        })
        self.assertEqual(response.status_code, 302)
        task = Task.objects.get(title='Due task')
        self.assertEqual(task.user, self.user)
        self.assertIsNotNone(task.due_date)

    def test_dashboard_shows_only_current_users_tasks(self):
        _make_task(self.user, 'Alice task', 'pending')
        _make_task(self.other_user, 'Bob task', 'completed')

        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice task')
        self.assertNotContains(response, 'Bob task')

    def test_dashboard_shows_empty_state_when_no_tasks(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No tasks found')

    def test_update_own_task(self):
        task = _make_task(self.user, 'Original')

        response = self.client.post(reverse('tasks:task_update', args=[task.pk]), {
            'title': 'Updated title',
            'description': 'Updated description',
            'status': 'completed',
            'due_date': '2027-02-02',
        })

        self.assertRedirects(response, reverse('tasks:dashboard'))
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated title')
        self.assertEqual(task.description, 'Updated description')
        self.assertEqual(task.status, 'completed')
        self.assertEqual(task.user, self.user)

    def test_delete_own_task(self):
        task = _make_task(self.user, 'To delete')

        response = self.client.post(reverse('tasks:task_delete', args=[task.pk]))

        self.assertRedirects(response, reverse('tasks:dashboard'))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_task_is_post_only(self):
        task = _make_task(self.user, 'Protected')
        response = self.client.get(reverse('tasks:task_delete', args=[task.pk]))
        # Confirmation page renders; deletion requires POST.
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())


class TaskStatusFilterTests(TaskSetupMixin, TestCase):
    """Filtering by incomplete and completed must work against own tasks."""

    def test_incomplete_filter_shows_only_pending_tasks(self):
        pending = _make_task(self.user, 'Pending task', 'pending')
        _make_task(self.user, 'Completed task', 'completed')
        _make_task(self.other_user, 'Other pending task', 'pending')

        response = self.client.get(
            f"{reverse('tasks:dashboard')}?status=incomplete"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending task')
        self.assertNotContains(response, 'Completed task')
        self.assertNotContains(response, 'Other pending task')

    def test_completed_filter_shows_only_completed_tasks(self):
        pending = _make_task(self.user, 'Pending task', 'pending')
        _make_task(self.user, 'Completed task', 'completed')

        response = self.client.get(
            f"{reverse('tasks:dashboard')}?status=completed"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed task')
        self.assertNotContains(response, 'Pending task')

    def test_all_filter_shows_own_tasks_of_both_statuses(self):
        _make_task(self.user, 'Pending task', 'pending')
        _make_task(self.user, 'Completed task', 'completed')

        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending task')
        self.assertContains(response, 'Completed task')

    def test_invalid_status_filter_shows_all_own_tasks(self):
        _make_task(self.user, 'Pending task', 'pending')

        response = self.client.get(
            f"{reverse('tasks:dashboard')}?status=nonsense"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pending task')


class TaskOwnershipIsolationTests(TaskSetupMixin, TestCase):
    """A user must not access another user's task by URL/ID manipulation."""

    def test_user_a_cannot_view_user_b_task_detail(self):
        task = _make_task(self.other_user, 'Bob task', 'pending')

        response = self.client.get(reverse('tasks:task_detail', args=[task.pk]))
        self.assertEqual(response.status_code, 404)

    def test_user_a_cannot_edit_user_b_task(self):
        task = _make_task(self.other_user, 'Bob task', 'pending')

        response = self.client.post(reverse('tasks:task_update', args=[task.pk]), {
            'title': 'Tampered',
            'description': 'Tampered description',
            'status': 'completed',
        })
        self.assertEqual(response.status_code, 404)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Bob task')
        self.assertEqual(task.status, 'pending')

    def test_user_a_cannot_delete_user_b_task(self):
        task = _make_task(self.other_user, 'Bob task', 'pending')

        response = self.client.post(reverse('tasks:task_delete', args=[task.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_nonexistent_task_returns_404(self):
        response = self.client.get(reverse('tasks:task_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class TaskAnonymousAccessTests(TestCase):
    """Anonymous users must be redirected to login for task operations."""

    def setUp(self):
        self.client = Client()
        self.url_login = reverse('tasks:login')

    def test_anonymous_cannot_create_task(self):
        response = self.client.get(reverse('tasks:task_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url_login, response.url)

    def test_anonymous_cannot_access_dashboard(self):
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.url_login, response.url)


class TaskInvalidInputTests(TaskSetupMixin, TestCase):
    """Invalid input must be handled safely without crashes or bad records."""

    def test_create_with_empty_title_does_not_create_record(self):
        response = self.client.post(reverse('tasks:task_create'), {
            'title': '',
            'description': 'No title',
            'status': 'pending',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.context['form'].errors)
        self.assertFalse(
            Task.objects.filter(title='', description='No title').exists()
        )

    def test_create_with_invalid_status_does_not_create_record(self):
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'Bad status',
            'status': 'not-a-status',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', response.context['form'].errors)
        self.assertFalse(Task.objects.filter(title='Bad status').exists())

    def test_create_with_invalid_due_date_format_does_not_create_record(self):
        response = self.client.post(reverse('tasks:task_create'), {
            'title': 'Bad date',
            'due_date': 'not-a-date',
            'status': 'pending',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('due_date', response.context['form'].errors)
        self.assertFalse(Task.objects.filter(title='Bad date').exists())

    def test_update_with_empty_title_keeps_existing_record(self):
        task = _make_task(self.user, 'Existing')
        response = self.client.post(reverse('tasks:task_update', args=[task.pk]), {
            'title': '',
            'description': task.description,
            'status': task.status,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.context['form'].errors)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Existing')

class TaskUiFlowTests(TaskSetupMixin, TestCase):
    """Task list and dashboard controls use owned PostgreSQL records."""

    def test_dashboard_counts_only_owned_tasks_and_upcoming_dates(self):
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        Task.objects.create(user=self.user, title='Due now', due_date=today, status='pending')
        Task.objects.create(user=self.user, title='Due later', due_date=today + timedelta(days=10), status='pending')
        Task.objects.create(user=self.user, title='Finished', status='completed')
        Task.objects.create(user=self.other_user, title='Private due task', due_date=today, status='pending')
        response = self.client.get(reverse('tasks:dashboard'))
        self.assertEqual(response.context['pending_count'], 2)
        self.assertEqual(response.context['due_soon_count'], 1)
        self.assertEqual(response.context['completed_count'], 1)
        self.assertNotContains(response, 'Private due task')

    def test_task_list_search_and_status_filter(self):
        _make_task(self.user, 'Write report', 'pending')
        _make_task(self.user, 'Write archive', 'completed')
        _make_task(self.other_user, 'Write private', 'pending')
        response = self.client.get(reverse('tasks:task_list'), {'q': 'Write', 'status': 'incomplete'})
        self.assertContains(response, 'Write report')
        self.assertNotContains(response, 'Write archive')
        self.assertNotContains(response, 'Write private')

    def test_toggle_requires_post_and_owner(self):
        own = _make_task(self.user, 'Own task', 'pending')
        other = _make_task(self.other_user, 'Other task', 'pending')
        url = reverse('tasks:task_toggle', args=[own.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(reverse('tasks:task_toggle', args=[other.pk])).status_code, 404)
        self.assertRedirects(self.client.post(url, {'next': reverse('tasks:task_list')}), reverse('tasks:task_list'))
        own.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(own.status, 'completed')
        self.assertEqual(other.status, 'pending')
