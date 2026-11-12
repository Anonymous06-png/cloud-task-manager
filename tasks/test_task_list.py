"""Focused Task List search and UI-04 translation regressions."""
from datetime import timedelta
from unittest import skipUnless

from django.contrib.auth.models import User
from django.db import connection
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Task


class TaskListSearchTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='list-search-owner')
        self.other = User.objects.create_user(username='list-search-other')
        self.client.force_login(self.owner)
        self.url = reverse('tasks:task_list')
        self.task = Task.objects.create(
            user=self.owner,
            title='Điện toán đám mây',
            due_date=timezone.localdate() - timedelta(days=1),
        )

    def test_exact_and_partial_vietnamese_title_searches(self):
        for query in ('Điện toán đám mây', 'toán đám', 'mây'):
            with self.subTest(query=query):
                response = self.client.get(self.url, {'q': query})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(list(response.context['tasks']), [self.task])
                self.assertEqual(response.context['page'].paginator.count, 1)

    @skipUnless(connection.vendor == 'postgresql', 'Unicode case conversion requires the PostgreSQL/ICU search branch')
    def test_postgresql_unicode_case_variants(self):
        for query in ('điện toán đám mây', 'ĐIỆN TOÁN ĐÁM MÂY', 'điện', 'ĐÁM MÂY'):
            with self.subTest(query=query):
                response = self.client.get(self.url, {'q': query})
                self.assertEqual(list(response.context['tasks']), [self.task])

    def test_nonmatching_and_blank_queries(self):
        response = self.client.get(self.url, {'q': 'không có kết quả này'})
        self.assertEqual(response.context['page'].paginator.count, 0)
        self.assertContains(response, 'class="empty-state"')
        response = self.client.get(self.url, {'q': '   '})
        self.assertEqual(response.context['query'], '')
        self.assertEqual(list(response.context['tasks']), [self.task])

    def test_search_never_exposes_other_owners_tasks(self):
        Task.objects.create(user=self.other, title=self.task.title)
        Task.objects.create(user=self.other, title='Bí mật chỉ người khác thấy')
        response = self.client.get(self.url, {'q': self.task.title})
        self.assertEqual(list(response.context['tasks']), [self.task])
        response = self.client.get(self.url, {'q': 'Bí mật'})
        self.assertEqual(response.context['page'].paginator.count, 0)

    def test_search_combines_with_each_existing_status_filter(self):
        done = Task.objects.create(user=self.owner, title=self.task.title, status='completed')
        Task.objects.create(user=self.other, title=self.task.title, status='completed')
        # Follow the existing model order, including equal creation timestamps.
        all_matches = list(self.owner.tasks.all())
        for status, expected in (('', all_matches), ('incomplete', [self.task]), ('completed', [done])):
            with self.subTest(status=status):
                response = self.client.get(self.url, {'q': self.task.title, 'status': status})
                self.assertEqual(list(response.context['tasks']), expected)
                self.assertEqual(response.context['page'].paginator.count, len(expected))
                if status:
                    self.assertContains(response, f'name="status" value="{status}"')

    def test_search_keeps_seven_row_pagination_and_existing_order(self):
        for index in range(9):
            Task.objects.create(user=self.owner, title=f'Điện toán đám mây {index}')
        Task.objects.create(user=self.owner, title=self.task.title, status='completed')
        expected = list(self.owner.tasks.filter(status='pending'))
        for number, start, stop in ((1, 0, 7), (2, 7, 10)):
            response = self.client.get(self.url, {
                'q': self.task.title, 'status': 'incomplete', 'page': number,
            })
            self.assertEqual(response.context['page'].paginator.count, 10)
            self.assertEqual(list(response.context['tasks']), expected[start:stop])
            self.assertContains(response, 'status=incomplete&amp;q=')
            self.assertContains(response, 'page=2' if number == 1 else 'page=1')

    def test_search_treats_sql_wildcards_and_quotes_as_literal_text(self):
        literal = Task.objects.create(user=self.owner, title="100%_\\ 'literal'")
        for query in ('%', '_', '\\', "'literal'"):
            response = self.client.get(self.url, {'q': query})
            self.assertEqual(list(response.context['tasks']), [literal])
        response = self.client.get(self.url, {'q': "' OR 1=1 --"})
        self.assertEqual(response.context['page'].paginator.count, 0)

    def test_invalid_status_page_and_query_length_remain_supported(self):
        response = self.client.get(self.url, {
            'q': self.task.title, 'status': 'invalid', 'page': 'invalid',
        })
        self.assertEqual(response.context['status_filter'], '')
        self.assertEqual(response.context['page'].number, 1)
        self.assertEqual(list(response.context['tasks']), [self.task])
        response = self.client.get(self.url, {'q': 'x' * 101})
        self.assertEqual(response.context['query'], 'x' * 100)

    def test_vi_en_group_overdue_and_clear_search_labels(self):
        for language, heading, overdue, clear in (
            ('vi', 'Quá hạn &amp; Đang làm', 'Quá hạn', 'Xóa tìm kiếm'),
            ('en', 'Overdue &amp; Incomplete', 'Overdue', 'Clear search'),
        ):
            with self.subTest(language=language):
                self.client.cookies['django_language'] = language
                response = self.client.get(self.url, {'q': self.task.title, 'status': 'incomplete'})
                self.assertContains(response, f'<html lang="{language}">')
                self.assertContains(response, heading)
                self.assertContains(response, f'<span class="overdue-label">{overdue}</span>')
                self.assertContains(response, clear)
                self.assertContains(response, 'href="/tasks/?status=incomplete"')
                if language == 'vi':
                    self.assertNotContains(response, 'Overdue')
                    self.assertNotContains(response, 'Clear search')

    def test_search_result_retains_csrf_and_return_path(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = client.get(self.url, {'q': self.task.title, 'status': 'incomplete'})
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'name="next"')
        toggle = reverse('tasks:task_toggle', args=[self.task.pk])
        self.assertContains(response, f'action="{toggle}"')
        self.assertEqual(client.post(toggle).status_code, 403)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'pending')
