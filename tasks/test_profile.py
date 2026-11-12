"""UI-07A: owner-only personal data, forms, CSRF, PRG and escaped VI/EN UI."""
from datetime import date, timedelta
from html.parser import HTMLParser

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from .models import Profile


class ProfileInputs(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.inputs = {}
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'input':
            self.inputs[attrs.get('name')] = attrs
        if tag == 'a':
            self.links.append(attrs)


class ProfileTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username='profile-owner', first_name='Existing', last_name='Name',
            email='owner@example.test',
        )
        cls.other = get_user_model().objects.create_user(
            username='other-owner', first_name='Other', email='other@example.test',
        )
        cls.other_profile = Profile.objects.create(
            user=cls.other, display_name='Private other name', date_of_birth=date(1980, 2, 1),
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'en'
        self.view_url = reverse('tasks:profile')
        self.edit_url = reverse('tasks:profile_edit')

    def test_anonymous_get_and_post_require_login(self):
        self.client.logout()
        for url in (self.view_url, self.edit_url):
            for method in ('get', 'post'):
                with self.subTest(url=url, method=method):
                    response = getattr(self.client, method)(url)
                    self.assertRedirects(response, f'/login/?next={url}', fetch_redirect_response=False)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_view_and_edit_get_do_not_create_profile(self):
        for url, template in ((self.view_url, 'profile.html'), (self.edit_url, 'profile_edit.html')):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, template)
            for text in ('Existing Name', '@profile-owner', 'owner@example.test'):
                self.assertContains(response, text)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_missing_name_and_email_have_real_fallbacks(self):
        self.user.first_name = self.user.last_name = self.user.email = ''
        self.user.save()
        response = self.client.get(self.view_url)
        self.assertContains(response, 'Not provided')
        self.assertContains(response, 'profile-owner')
        form = self.client.get(self.edit_url).context['form']
        self.assertEqual(form['display_name'].value(), 'profile-owner')

    def test_view_is_read_only_and_rejects_post(self):
        response = self.client.get(self.view_url)
        markup = ProfileInputs(response.content.decode().split('<main ', 1)[1].split('</main>', 1)[0])
        self.assertFalse(markup.inputs)
        self.assertIn(self.edit_url, [link['href'] for link in markup.links])
        self.assertEqual(self.client.post(self.view_url, {'display_name': 'No write'}).status_code, 405)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_edit_fields_are_explicit_and_accessible(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(set(response.context['form'].fields), {'display_name', 'date_of_birth'})
        markup = ProfileInputs(response.content.decode())
        name = markup.inputs['display_name']
        self.assertEqual(name['maxlength'], '50')
        self.assertEqual(name['minlength'], '2')
        self.assertIn('required', name)
        dob = markup.inputs['date_of_birth']
        self.assertEqual(dob['type'], 'date')
        self.assertNotIn('required', dob)
        for field in ('display_name', 'date_of_birth'):
            self.assertContains(response, f'for="id_{field}"')
            self.assertEqual(markup.inputs[field]['aria-describedby'], f'id_{field}_helptext')
        self.assertContains(response, f'href="{self.view_url}"')
        self.assertNotIn('username', markup.inputs)
        self.assertNotIn('email', markup.inputs)

    def test_valid_save_redirects_and_persists_after_new_login(self):
        response = self.client.post(self.edit_url, {'display_name': '  Nguyễn An  ', 'date_of_birth': '2000-02-29'})
        self.assertRedirects(response, self.view_url)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.display_name, 'Nguyễn An')
        self.assertEqual(profile.date_of_birth, date(2000, 2, 29))
        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.get(self.view_url)
        self.assertContains(response, 'Nguyễn An')
        self.assertContains(response, 'datetime="2000-02-29"')
        form = self.client.get(self.edit_url).context['form']
        self.assertEqual(form['display_name'].value(), 'Nguyễn An')
        self.assertEqual(form['date_of_birth'].value(), date(2000, 2, 29))

    def test_success_message_and_get_refresh_do_not_duplicate_writes(self):
        response = self.client.post(self.edit_url, {'display_name': 'Saved name'}, follow=True)
        self.assertEqual(response.redirect_chain, [(self.view_url, 302)])
        self.assertContains(response, 'Profile updated.')
        self.client.get(self.view_url)
        self.assertEqual(Profile.objects.filter(user=self.user).count(), 1)

    def test_cancel_returns_to_profile_without_writing(self):
        response = self.client.get(self.edit_url)
        self.assertContains(response, f'<a class="btn secondary" href="{self.view_url}">Cancel</a>', html=True)
        self.assertEqual(self.client.get(self.view_url).status_code, 200)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_header_language_switch_uses_csrf_cookie_and_returns_to_edit(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.get(self.edit_url)
        token = ProfileInputs(response.content.decode()).inputs['csrfmiddlewaretoken']['value']
        response = client.post(reverse('set_language'), {
            'language': 'en', 'next': self.edit_url, 'csrfmiddlewaretoken': token,
        })
        self.assertRedirects(response, self.edit_url)
        self.assertEqual(client.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'en')
        self.assertContains(client.get(self.edit_url), 'Edit Profile')
        self.assertEqual(int(client.session['_auth_user_id']), self.user.pk)
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_optional_date_can_be_omitted_and_cleared(self):
        for value in (None, '1999-01-01', ''):
            payload = {'display_name': 'Saved name'}
            if value is not None:
                payload['date_of_birth'] = value
            self.assertRedirects(self.client.post(self.edit_url, payload), self.view_url)
            self.assertEqual(Profile.objects.get(user=self.user).date_of_birth,
                             date(1999, 1, 1) if value else None)

    def test_display_name_length_boundaries(self):
        for value in ('AB', 'Đ' * 50):
            with self.subTest(length=len(value)):
                self.assertRedirects(self.client.post(self.edit_url, {'display_name': value}), self.view_url)
                self.assertEqual(Profile.objects.get(user=self.user).display_name, value)

    def test_invalid_names_and_dates_never_create_profile(self):
        cases = (
            ({}, 'display_name'), ({'display_name': ''}, 'display_name'),
            ({'display_name': '   '}, 'display_name'), ({'display_name': ' A '}, 'display_name'),
            ({'display_name': 'x' * 51}, 'display_name'),
            ({'display_name': 'Valid name', 'date_of_birth': '2001-02-29'}, 'date_of_birth'),
            ({'display_name': 'Valid name', 'date_of_birth': 'not-a-date'}, 'date_of_birth'),
            ({'display_name': 'Valid name', 'date_of_birth': '01/02/2000'}, 'date_of_birth'),
            ({'display_name': 'Valid name', 'date_of_birth': (timezone.localdate() + timedelta(days=1)).isoformat()}, 'date_of_birth'),
        )
        for payload, field in cases:
            with self.subTest(payload=payload):
                response = self.client.post(self.edit_url, payload)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context['form'].errors)
                self.assertContains(response, 'Your changes have not been saved.')
                self.assertContains(response, 'role="alert"')
                self.assertContains(response, 'aria-invalid="true"')
                markup = ProfileInputs(response.content.decode())
                self.assertIn(f'id_{field}_error', markup.inputs[field]['aria-describedby'])
                self.assertFalse(Profile.objects.filter(user=self.user).exists())

    def test_invalid_edit_preserves_saved_values_and_bound_input(self):
        profile = Profile.objects.create(user=self.user, display_name='Original', date_of_birth=date(1990, 1, 1))
        response = self.client.post(self.edit_url, {'display_name': 'Changed name', 'date_of_birth': 'bad-date'})
        self.assertEqual(response.context['form']['display_name'].value(), 'Changed name')
        profile.refresh_from_db()
        self.assertEqual(profile.display_name, 'Original')
        self.assertEqual(profile.date_of_birth, date(1990, 1, 1))

    def test_today_is_allowed_without_age_restriction(self):
        response = self.client.post(self.edit_url, {'display_name': 'Valid name', 'date_of_birth': timezone.localdate().isoformat()})
        self.assertRedirects(response, self.view_url)

    def test_other_account_identifiers_cannot_select_a_profile(self):
        query = f'?user_id={self.other.pk}&pk={self.other_profile.pk}&username={self.other.username}'
        for url in (self.view_url, self.edit_url):
            response = self.client.get(url + query)
            self.assertContains(response, 'Existing Name')
            self.assertNotContains(response, 'Private other name')
            self.assertNotContains(response, 'other@example.test')
        for url in (f'/profile/{self.other.pk}/', f'/profile/{self.other.pk}/edit/'):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_forged_post_ignores_owner_and_authentication_fields(self):
        from allauth.account.models import EmailAddress
        from allauth.socialaccount.models import SocialAccount

        social = SocialAccount.objects.create(user=self.user, provider='google', uid='profile-test-google-id')
        email = EmailAddress.objects.create(user=self.user, email=self.user.email, verified=True, primary=True)
        original_password = self.user.password
        response = self.client.post(self.edit_url, {
            'display_name': 'Only own name', 'date_of_birth': '1990-01-01',
            'user': self.other.pk, 'user_id': self.other.pk, 'id': self.other_profile.pk,
            'username': 'hijacked', 'email': 'hijacked@example.test',
            'first_name': 'Replaced', 'last_name': 'Replaced',
            'password': 'Replaced', 'provider': 'Replaced', 'next': 'https://evil.example/',
        })
        self.assertRedirects(response, self.view_url)
        self.user.refresh_from_db()
        self.assertEqual((self.user.username, self.user.email, self.user.first_name, self.user.last_name, self.user.password),
                         ('profile-owner', 'owner@example.test', 'Existing', 'Name', original_password))
        self.other_profile.refresh_from_db()
        self.assertEqual(self.other_profile.display_name, 'Private other name')
        self.assertEqual(self.other_profile.date_of_birth, date(1980, 2, 1))
        self.assertEqual(Profile.objects.get(user=self.user).display_name, 'Only own name')
        social.refresh_from_db()
        email.refresh_from_db()
        self.assertEqual((social.provider, social.uid, social.user_id), ('google', 'profile-test-google-id', self.user.pk))
        self.assertEqual((email.email, email.verified), ('owner@example.test', True))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_missing_or_wrong_csrf_is_rejected_then_real_token_saves(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.get(self.edit_url)
        token = ProfileInputs(response.content.decode()).inputs['csrfmiddlewaretoken']['value']
        for extra in ({}, {'csrfmiddlewaretoken': 'x' * 64}):
            rejected = client.post(self.edit_url, {'display_name': 'Rejected name', **extra})
            self.assertEqual(rejected.status_code, 403)
            self.assertFalse(Profile.objects.filter(user=self.user).exists())
            self.assertIn('_auth_user_id', client.session)
        self.assertRedirects(client.post(self.edit_url, {'display_name': 'CSRF saved', 'csrfmiddlewaretoken': token}), self.view_url)

    def test_escaping_in_view_edit_sidebar_and_invalid_submission(self):
        name = '<script>alert("X")</script> & <b>A</b>'
        self.user.username = '<img-onerror=x>'
        self.user.email = '\"><script>email</script>@example.test'
        self.user.save()
        self.assertRedirects(self.client.post(self.edit_url, {'display_name': name}), self.view_url)
        for url in (self.view_url, self.edit_url, reverse('tasks:settings')):
            response = self.client.get(url)
            for value in (name, self.user.username, self.user.email):
                self.assertContains(response, escape(value))
                self.assertNotContains(response, value)
        response = self.client.post(self.edit_url, {'display_name': name, 'date_of_birth': 'bad-date'})
        self.assertContains(response, escape(name))
        self.assertNotContains(response, name)

    def test_vi_en_copy_validation_and_success(self):
        for language, title, error, success in (
            ('en', 'Edit Profile', 'Use between 2 and 50 characters.', 'Profile updated.'),
            ('vi', 'Chỉnh sửa hồ sơ', 'Sử dụng từ 2 đến 50 ký tự.', 'Đã cập nhật hồ sơ.'),
        ):
            with self.subTest(language=language):
                self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = language
                self.assertContains(self.client.get(self.edit_url), title)
                self.assertContains(self.client.post(self.edit_url, {'display_name': 'A'}), error)
                self.assertContains(self.client.post(self.edit_url, {'display_name': 'Valid name'}, follow=True), success)

    def test_saved_name_is_used_by_dropdown_and_settings(self):
        self.client.post(self.edit_url, {'display_name': 'New personal name'})
        for page in ('profile', 'profile_edit', 'dashboard', 'settings'):
            response = self.client.get(reverse(f'tasks:{page}'))
            sidebar = response.content.decode().split('<aside ', 1)[1].split('</aside>', 1)[0]
            self.assertIn('New personal name', sidebar)
        self.assertContains(self.client.get(reverse('tasks:settings')), 'class="settings-account-name">New personal name</p>')

    def test_no_demo_assets_or_unsupported_claims(self):
        for url in (self.view_url, self.edit_url):
            html = self.client.get(url).content.decode().split('<main ', 1)[1].split('</main>', 1)[0]
            for forbidden in ('Upload new image', 'SunnyEternity',
                              'cdn.tailwindcss.com', 'fonts.googleapis.com', 'age verification', 'Contact support',
                              'all your Flowspace workspaces', 'Esc to discard', 'href="#"'):
                self.assertNotIn(forbidden, html)
            self.assertIn('class="profile-initials" aria-hidden="true">PR</span>', html)

    def test_edit_rejects_unsupported_http_methods(self):
        for method in ('put', 'patch', 'delete'):
            self.assertEqual(getattr(self.client, method)(self.edit_url).status_code, 405)

    def test_one_to_one_and_model_name_validation(self):
        Profile.objects.create(user=self.user, display_name='Valid name')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Profile.objects.create(user=self.user, display_name='Duplicate')
        with self.assertRaises(ValidationError):
            Profile(user=self.other, display_name='X').full_clean()
        user_id = self.user.pk
        self.user.delete()
        self.assertFalse(Profile.objects.filter(user_id=user_id).exists())
