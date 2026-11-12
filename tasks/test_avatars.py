"""Owner-only avatar storage/validation and Settings navigation regressions."""
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Profile


def picture(fmt='PNG', name='photo.png', size=(16, 12)):
    output = BytesIO()
    Image.new('RGB', size, 'red').save(output, fmt)
    return SimpleUploadedFile(name, output.getvalue(), content_type='application/octet-stream')


class AvatarTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.media = tempfile.TemporaryDirectory(prefix='ui07b-media-')
        cls.override = override_settings(MEDIA_ROOT=cls.media.name)
        cls.override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.override.disable()
        cls.media.cleanup()
        super().tearDownClass()

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='avatar-owner', first_name='Existing', last_name='Name', email='avatar@example.test')
        self.other = get_user_model().objects.create_user(username='other-owner')
        self.profile = Profile.objects.create(user=self.user, display_name='Saved name')
        self.client.force_login(self.user)
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'en'
        self.url = reverse('tasks:profile_avatar')
        self.image_url = reverse('tasks:profile_avatar_image')

    def upload(self, image=None, **extra):
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, {'action': 'upload', 'avatar': image or picture(), **extra})
        self.profile = Profile.objects.get(user=self.user)
        return response

    def test_supported_formats_are_reencoded_and_persisted(self):
        for fmt, name in (('JPEG', 'a.jpg'), ('PNG', 'b.png'), ('WEBP', 'c.webp')):
            response = self.upload(picture(fmt, name))
            self.assertRedirects(response, reverse('tasks:profile_edit'))
            self.assertRegex(self.profile.avatar.name, r'^avatars/[a-f0-9]{32}\.png$')
            with self.profile.avatar.open('rb') as stored:
                image = Image.open(stored)
                self.assertEqual(image.format, 'PNG')
                self.assertFalse(image.info)
            self.assertEqual(self.profile.display_name, 'Saved name')

    def test_change_and_remove_delete_only_own_old_file(self):
        self.upload()
        old = self.profile.avatar.path
        self.upload(picture(name='same.png'))
        current = self.profile.avatar.path
        self.assertNotEqual(old, current)
        self.assertFalse(Path(old).exists())
        other = Profile.objects.create(user=self.other, display_name='Other')
        other.avatar.save('other.png', picture())
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(self.url, {'action': 'remove', 'user_id': self.other.pk})
        self.assertRedirects(response, reverse('tasks:profile_edit'))
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.avatar)
        self.assertFalse(Path(current).exists())
        self.assertTrue(Path(other.avatar.path).exists())

    def test_invalid_inputs_preserve_old_avatar(self):
        self.upload()
        old = self.profile.avatar.name
        old_bytes = Path(self.profile.avatar.path).read_bytes()
        for file in (
            SimpleUploadedFile('fake.png', b'not an image', content_type='image/png'),
            SimpleUploadedFile('vector.svg', b'<svg xmlns="http://www.w3.org/2000/svg"/>'),
            SimpleUploadedFile('too-big.png', b'x' * (2 * 1024 * 1024 + 1)),
            picture('GIF', 'a.png'), picture('BMP', 'a.png'), picture(name='executable.exe'),
            SimpleUploadedFile('truncated.png', picture().read()[:35]),
            picture(size=(4097, 1)),
        ):
            with self.subTest(name=file.name):
                self.assertEqual(self.upload(file).status_code, 200)
                self.assertEqual(self.profile.avatar.name, old)
                self.assertEqual(Path(self.profile.avatar.path).read_bytes(), old_bytes)

    def test_exact_byte_limit_and_actual_bytes_are_checked(self):
        raw = picture().read()
        self.assertEqual(self.upload(SimpleUploadedFile('ok.png', raw + b'\0' * (2 * 1024 * 1024 - len(raw)))).status_code, 302)
        self.assertLess(self.profile.avatar.size, 2 * 1024 * 1024)

    def test_payload_and_original_filename_are_not_stored(self):
        raw = picture().read() + b'<script>alert(1)</script>'
        self.upload(SimpleUploadedFile('../../evil.php.png', raw))
        self.assertNotIn('evil', self.profile.avatar.name)
        self.assertNotIn(b'<script>', Path(self.profile.avatar.path).read_bytes())

    def test_thumbnail_is_bounded(self):
        self.upload(picture(size=(1200, 600)))
        with self.profile.avatar.open('rb') as file:
            self.assertEqual(Image.open(file).size, (512, 256))

    def test_missing_file_is_error_and_remove_empty_is_safe(self):
        self.assertEqual(self.client.post(self.url, {'action': 'upload'}).status_code, 200)
        self.assertRedirects(self.client.post(self.url, {'action': 'remove'}), reverse('tasks:profile_edit'))

    def test_anonymous_and_wrong_methods_cannot_mutate_or_read(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)
        self.client.logout()
        for url, method in ((self.url, 'post'), (self.image_url, 'get')):
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith('/login/'))

    def test_csrf_upload_and_removal(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        client.get(reverse('tasks:profile_edit'))
        for action in ('upload', 'remove'):
            self.assertEqual(client.post(self.url, {'action': action, 'avatar': picture()}).status_code, 403)
        self.assertEqual(client.post(self.url, {'action': 'upload', 'avatar': picture(), 'csrfmiddlewaretoken': client.cookies['csrftoken'].value}).status_code, 302)
        self.assertEqual(client.post(self.url, {'action': 'remove', 'csrfmiddlewaretoken': client.cookies['csrftoken'].value}).status_code, 302)

    def test_image_route_is_owner_only_and_never_public_media(self):
        self.upload()
        response = self.client.get(self.image_url + f'?user_id={self.other.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(b''.join(response.streaming_content), Path(self.profile.avatar.path).read_bytes())
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(self.image_url + f'?user_id={self.user.pk}').status_code, 404)
        self.assertEqual(self.client.get('/media/' + self.profile.avatar.name).status_code, 404)

    def test_forged_owner_and_account_fields_are_ignored(self):
        other = Profile.objects.create(user=self.other, display_name='Private other')
        self.upload(user=self.other.pk, user_id=self.other.pk, id=other.pk, display_name='Changed', email='bad@example.test')
        other.refresh_from_db()
        self.assertFalse(other.avatar)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'avatar@example.test')
        self.assertEqual(self.profile.display_name, 'Saved name')

    def test_avatars_render_in_all_requested_surfaces_then_fallback(self):
        self.upload()
        for page in ('profile', 'profile_edit', 'settings', 'dashboard'):
            response = self.client.get(reverse(f'tasks:{page}'))
            self.assertContains(response, f'src="{self.image_url}"')
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(self.url, {'action': 'remove'})
        response = self.client.get(reverse('tasks:profile'))
        self.assertContains(response, 'class="profile-initials" aria-hidden="true">AV</span>')
        self.assertNotContains(response, f'src="{self.image_url}"')

    def test_avatar_only_profile_preserves_existing_account_name(self):
        self.profile.delete()
        self.upload()
        self.assertEqual(self.profile.display_name, '')
        response = self.client.get(reverse('tasks:profile_edit'))
        self.assertEqual(response.context['form']['display_name'].value(), 'Existing Name')

    def test_settings_navigation_in_both_languages(self):
        for language, label in (('en', 'View Profile'), ('vi', 'Xem hồ sơ')):
            self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = language
            response = self.client.get(reverse('tasks:settings'))
            self.assertContains(response, label)
            self.assertContains(response, f'class="settings-profile-link" href="{reverse("tasks:profile")}"')
            self.assertContains(response, 'data-theme-choice')
            self.assertContains(response, 'action="/i18n/setlang/"')

    def test_details_save_preserves_avatar_and_avatar_preserves_birth_date(self):
        from datetime import date
        self.profile.date_of_birth = date(2000, 1, 2)
        self.profile.save()
        self.upload()
        self.assertEqual(self.profile.date_of_birth, date(2000, 1, 2))
        name = self.profile.avatar.name
        self.assertRedirects(self.client.post(reverse('tasks:profile_edit'), {
            'display_name': 'New name', 'date_of_birth': '2000-01-02',
        }), reverse('tasks:profile'))
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.avatar.name, name)
        self.client.logout()
        self.client.force_login(self.user)
        self.assertContains(self.client.get(reverse('tasks:profile')), f'src="{self.image_url}"')

    def test_old_file_deletion_is_deferred_to_commit(self):
        self.upload()
        old = self.profile.avatar.path
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            self.client.post(self.url, {'action': 'upload', 'avatar': picture()})
        self.assertTrue(Path(old).exists())
        self.assertEqual(len(callbacks), 1)
        callbacks[0]()
        self.assertFalse(Path(old).exists())

    def test_vietnamese_upload_error_and_success(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = 'vi'
        self.assertContains(self.upload(SimpleUploadedFile('a.svg', b'<svg/>')), 'Chọn ảnh JPG, PNG hoặc WebP hợp lệ.')
        response = self.client.post(self.url, {'action': 'upload', 'avatar': picture()}, follow=True)
        self.assertContains(response, 'Đã cập nhật ảnh đại diện.')

    def test_storage_is_cleaned_if_db_save_fails(self):
        self.upload()
        before = set(Path(self.media.name).rglob('*.png'))
        old = self.profile.avatar.name
        with patch.object(Profile, 'save', side_effect=RuntimeError('simulated database failure')):
            with self.assertRaises(RuntimeError):
                self.upload()
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.avatar.name, old)
        self.assertEqual(set(Path(self.media.name).rglob('*.png')), before)
