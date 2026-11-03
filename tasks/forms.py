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

from .models import Task


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
