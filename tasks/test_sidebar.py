"""Focused UI-11 account disclosure and real session/logout regressions."""
import re
from html.parser import HTMLParser

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class SidebarMarkup(HTMLParser):
    """Collect normal sidebar markup separately from the no-JS fallback."""

    def __init__(self, html):
        super().__init__()
        self.nodes = []
        self.in_sidebar = False
        self.in_noscript = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'aside' and attrs.get('id') == 'workspace-sidebar':
            self.in_sidebar = True
        if tag == 'noscript':
            self.in_noscript = True
        if self.in_sidebar:
            self.nodes.append((tag, attrs, self.in_noscript))

    def handle_endtag(self, tag):
        if tag == 'aside':
            self.in_sidebar = False
        if tag == 'noscript':
            self.in_noscript = False

    def find(self, tag, fallback=False, **attrs):
        return [node for node_tag, node, no_js in self.nodes
                if node_tag == tag and no_js == fallback
                and all(node.get(key) == value for key, value in attrs.items())]


class AccountSidebarTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='sidebar-user', password='Sidebar-test-password-2031!',
            first_name='An <script>', last_name='& Team', email='an@example.test',
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_account_on_existing_pages_in_both_languages(self):
        for language, profile, logout in (
            ('en', 'My Profile', 'Log out of this session'),
            ('vi', 'Hồ sơ cá nhân', 'Đăng xuất khỏi phiên này'),
        ):
            for page in ('dashboard', 'task_list', 'settings'):
                with self.subTest(language=language, page=page):
                    self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = language
                    response = self.client.get(reverse(f'tasks:{page}'), HTTP_ACCEPT_LANGUAGE=language)
                    self.assertEqual(response.status_code, 200)
                    html = response.content.decode()
                    sidebar = html.split('<aside ', 1)[1].split('</aside>', 1)[0]
                    for text in (profile, logout, 'An &lt;script&gt; &amp; Team',
                                 '@sidebar-user', 'an@example.test'):
                        self.assertIn(text, sidebar)
                    self.assertNotIn('An <script>', sidebar)
                    markup = SidebarMarkup(html)
                    trigger, = markup.find('button', id='account-trigger')
                    self.assertEqual(trigger['type'], 'button')
                    self.assertEqual(trigger['aria-expanded'], 'false')
                    self.assertEqual(trigger['aria-controls'], 'account-dropdown')
                    self.assertIn('hidden', trigger)
                    panel, = markup.find('section', id='account-dropdown')
                    self.assertIn('hidden', panel)
                    self.assertIn('inert', panel)
                    self.assertEqual(panel['aria-labelledby'], 'account-trigger')

    def test_no_duplicate_actions_or_fake_profile_link(self):
        response = self.client.get(reverse('tasks:dashboard'))
        markup = SidebarMarkup(response.content.decode())
        self.assertEqual(len(markup.find('a', href=reverse('tasks:settings'))), 1)
        forms = markup.find('form')
        self.assertEqual(len(forms), 1)
        self.assertEqual(forms[0]['method'], 'post')
        self.assertEqual(forms[0]['action'], reverse('tasks:logout'))
        profile, = markup.find('a', **{'class': 'account-action account-profile'})
        self.assertEqual(profile['href'], reverse('tasks:profile'))
        self.assertNotIn('aria-disabled', profile)
        self.assertFalse(markup.find('a', href=reverse('tasks:logout')))
        for node in markup.find('a'):
            self.assertNotIn(node['href'], ('#', '#profile', '#logout'))

    def test_optional_email_and_full_name_fallback(self):
        self.user.first_name = self.user.last_name = self.user.email = ''
        self.user.save()
        response = self.client.get(reverse('tasks:settings'))
        sidebar = response.content.decode().split('<aside ', 1)[1].split('</aside>', 1)[0]
        self.assertIn('class="account-name">sidebar-user</p>', sidebar)
        self.assertNotIn('an@example.test', sidebar)
        self.assertEqual(sidebar.count('class="account-meta"'), 1)

    def test_no_js_fallback_keeps_real_settings_and_csrf_logout(self):
        markup = SidebarMarkup(self.client.get(reverse('tasks:dashboard')).content.decode())
        self.assertEqual(len(markup.find('a', fallback=True, href=reverse('tasks:profile'))), 1)
        self.assertEqual(len(markup.find('a', fallback=True, href=reverse('tasks:settings'))), 1)
        form, = markup.find('form', fallback=True)
        self.assertEqual(form['method'], 'post')
        self.assertEqual(form['action'], reverse('tasks:logout'))
        self.assertEqual(len(markup.find('input', fallback=True, name='csrfmiddlewaretoken')), 1)
        self.assertEqual(len(markup.find('input', name='csrfmiddlewaretoken')), 1)

    def test_sidebar_logout_csrf_token_clears_real_session(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.get(reverse('tasks:dashboard'))
        markup = SidebarMarkup(response.content.decode())
        token, = markup.find('input', name='csrfmiddlewaretoken')
        self.assertTrue(re.fullmatch(r'[a-zA-Z0-9]{64}', token['value']))
        rejected = client.post(reverse('tasks:logout'))
        self.assertEqual(rejected.status_code, 403)
        self.assertIn('_auth_user_id', client.session)
        response = client.post(reverse('tasks:logout'), {'csrfmiddlewaretoken': token['value']})
        self.assertRedirects(response, reverse('tasks:login'))
        self.assertNotIn('_auth_user_id', client.session)

    def test_shell_navigation_and_fold_controls_remain(self):
        markup = SidebarMarkup(self.client.get(reverse('tasks:dashboard')).content.decode())
        for name in ('dashboard', 'task_list', 'task_create'):
            self.assertTrue(markup.find('a', href=reverse(f'tasks:{name}')))
        self.assertTrue(markup.find('a', href=reverse('tasks:task_list') + '?status=completed'))
        self.assertTrue(markup.find('use', href='#fold'))
        toggles = [node for node in markup.find('button') if 'data-sidebar-toggle' in node]
        self.assertEqual(len(toggles), 3)
        self.assertTrue(all(node['aria-controls'] == 'workspace-sidebar' for node in toggles))

    def test_anonymous_login_has_no_account_disclosure(self):
        self.client.logout()
        response = self.client.get(reverse('tasks:login'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="account-trigger"')
        self.assertNotContains(response, 'id="account-dropdown"')
