"""
Forms for the authentication flow.

Built on Django's built-in authentication forms so that the standard
validation rules (password length, password similarity, common/numeric
passwords and unique username) keep working without extra dependencies.
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Profile, Task
from .avatars import normalize_avatar


class AvatarForm(forms.Form):
    avatar = forms.FileField(
        label=_('Profile picture'),
        widget=forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png,.webp', 'aria-describedby': 'avatar-help'}),
    )

    def clean_avatar(self):
        return normalize_avatar(self.cleaned_data['avatar'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound and self.errors:
            self.fields['avatar'].widget.attrs['aria-describedby'] = 'avatar-help avatar-errors'


class ProfileForm(forms.ModelForm):
    """Only personal details are writable; the view supplies the owner."""

    display_name = forms.CharField(
        label=_('Display name'), min_length=2, max_length=50,
        help_text=_('Use between 2 and 50 characters.'),
        widget=forms.TextInput(attrs={'autocomplete': 'nickname', 'minlength': 2}),
        error_messages={
            'required': _('Enter a display name.'),
            'min_length': _('Use between 2 and 50 characters.'),
            'max_length': _('Use between 2 and 50 characters.'),
        },
    )
    date_of_birth = forms.DateField(
        label=_('Date of birth'), required=False, input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'autocomplete': 'bday'}),
        help_text=_('Optional. Leave blank if you prefer not to add it.'),
        error_messages={'invalid': _('Enter a valid date in YYYY-MM-DD format.')},
    )

    class Meta:
        model = Profile
        fields = ('display_name', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_birth'].widget.attrs['max'] = timezone.localdate().isoformat()
        for name, field in self.fields.items():
            field.widget.attrs['aria-describedby'] = f'id_{name}_helptext'
        # Associate errors explicitly as well as Django's aria-invalid marker.
        if self.is_bound:
            for name in self.errors:
                if name in self.fields:
                    self.fields[name].widget.attrs['aria-describedby'] += f' id_{name}_error'

    def clean_date_of_birth(self):
        value = self.cleaned_data['date_of_birth']
        if value and value > timezone.localdate():
            raise forms.ValidationError(_('Date of birth cannot be in the future.'))
        return value


class TaskForm(forms.ModelForm):
    """Create and update task fields with Django's standard validation."""

    class Meta:
        model = Task
        fields = ('title', 'description', 'due_date', 'status')
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'due_date': _('Due date'),
            'status': _('Status'),
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SignUpForm(UserCreationForm):
    """Registration form for new accounts.

    Adds an optional email field on top of Django's ``UserCreationForm``.
    Password validation and the duplicate-username check are inherited.
    """

    email = forms.EmailField(
        required=False,
        help_text=_('Optional. Used only to identify your account.'),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
