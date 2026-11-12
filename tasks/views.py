"""
Views for Cloud Task Manager - authentication flow.

Personal pages are protected with Django's ``login_required`` decorator and
all task querysets are scoped to the signed-in user.
"""
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import F, Value
from django.db.models.functions import Collate
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods

from .forms import AvatarForm, ProfileForm, SignUpForm, TaskForm
from .models import Profile, Task


def home(request):
    """Show the public workspace entry or resume the signed-in workspace."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    return render(request, 'home.html', {'project_name': 'Cloud Task Manager'})


def language_settings(request):
    """Render the language and appearance settings page."""
    return render(request, 'settings.html', {
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
    })


@login_required
@require_http_methods(['GET', 'HEAD'])
def profile_view(request):
    """No user identifier is accepted: this is always the signed-in account."""
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'profile.html', {'profile': profile})


@login_required
@require_http_methods(['GET', 'HEAD', 'POST'])
def profile_edit(request):
    profile = Profile.objects.filter(user=request.user).first()
    instance = profile or Profile(user=request.user)
    initial = {
        'display_name': instance.display_name or request.user.get_full_name() or request.user.username,
    }
    form = ProfileForm(
        request.POST if request.method == 'POST' else None,
        instance=instance, initial=initial,
    )
    if request.method == 'POST' and form.is_valid():
        if form.instance.pk:
            form.instance.save(update_fields=['display_name', 'date_of_birth'])
        else:
            form.save()
        messages.success(request, _('Profile updated.'))
        return redirect('tasks:profile')
    return render(request, 'profile_edit.html', {'form': form, 'avatar_form': AvatarForm()})


def _delete_avatar(storage, name):
    # Also safe if an account is edited twice before a transaction commits.
    if name and not Profile.objects.filter(avatar=name).exists():
        storage.delete(name)


@login_required
@require_POST
def profile_avatar(request):
    action = request.POST.get('action')
    form = AvatarForm(request.POST, request.FILES)
    if action not in {'upload', 'remove'}:
        raise Http404
    if action == 'upload' and not form.is_valid():
        profile = Profile.objects.filter(user=request.user).first()
        details = ProfileForm(instance=profile, initial={
            'display_name': (profile.display_name if profile else '') or request.user.get_full_name() or request.user.username,
        })
        return render(request, 'profile_edit.html', {'form': details, 'avatar_form': form})
    new_name = None
    storage = Profile._meta.get_field('avatar').storage
    try:
        with transaction.atomic():
            # Serialize first-avatar creation as well as replacement/removal.
            get_user_model().objects.select_for_update().get(pk=request.user.pk)
            profile, _created = Profile.objects.get_or_create(user=request.user)
            old_name = profile.avatar.name
            if action == 'upload':
                profile.avatar.save('avatar.png', form.cleaned_data['avatar'], save=False)
                new_name = profile.avatar.name
            else:
                profile.avatar = ''
            profile.save(update_fields=['avatar'])
            if old_name:
                transaction.on_commit(lambda: _delete_avatar(storage, old_name), robust=True)
    except Exception:
        if new_name:
            storage.delete(new_name)
        raise
    messages.success(request, _('Profile picture updated.'))
    return redirect('tasks:profile_edit')


@login_required
@require_http_methods(['GET', 'HEAD'])
def profile_avatar_image(request):
    profile = Profile.objects.filter(user=request.user).first()
    if not profile or not profile.avatar:
        raise Http404
    try:
        response = FileResponse(profile.avatar.open('rb'), content_type='image/png')
    except FileNotFoundError:
        raise Http404
    response['Cache-Control'] = 'private, no-store'
    response['X-Content-Type-Options'] = 'nosniff'
    return response


def health_check(request):
    """Health check endpoint for monitoring. Public, no authentication."""
    return JsonResponse({
        'status': 'ok',
        'service': 'cloud-task-manager',
        'version': '1.1.0-auth',
    })


def register(request):
    """Create a new account, then log the new user in."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # An explicit backend is required now that AUTHENTICATION_BACKENDS
            # also contains allauth's social login backend; registration must
            # always authenticate through the ModelBackend.
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, _('Account created. You are now signed in.'))
            return redirect('tasks:dashboard')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    """Render the authenticated user's overview using only their tasks."""
    status_filter = request.GET.get('status', '')
    if status_filter in {'incomplete', 'completed'}:
        return _task_list_response(request, status_filter)

    all_tasks = request.user.tasks.all()
    today = timezone.localdate()
    soon = today + timedelta(days=6)
    pending = all_tasks.filter(status='pending')
    completed = all_tasks.filter(status='completed')
    due_soon = pending.filter(
        due_date__gte=today,
        due_date__lte=soon,
    ).order_by('due_date', 'created_at')
    priority_tasks = list(
        pending.order_by(F('due_date').asc(nulls_last=True), '-created_at')[:5]
    )
    recent_completed = list(completed.order_by('-updated_at')[:5])
    completed_tasks = recent_completed[:5]

    context = {
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
        'tasks': all_tasks,
        'status_filter': '',
        'pending_count': pending.count(),
        'completed_count': completed.count(),
        'due_soon_count': due_soon.count(),
        'due_soon': due_soon[:4],
        'priority_tasks': priority_tasks,
        'completed_tasks': completed_tasks,
        'today': today,
        'today_task': due_soon.first(),
    }
    return render(request, 'dashboard.html', context)


def _task_list_response(request, status_filter='', template='task_list.html'):
    """Render the full task list while keeping all filters owner-scoped."""
    tasks = request.user.tasks.all()
    status_map = {'incomplete': 'pending', 'completed': 'completed'}
    if status_filter in status_map:
        tasks = tasks.filter(status=status_map[status_filter])
    else:
        status_filter = ''

    query = request.GET.get('q', '').strip()[:100]
    if query:
        if connection.vendor == 'postgresql':
            # C-locale UPPER() is ASCII-only. Collate both operands before
            # Django applies UPPER(), so Vietnamese Đ/đ and vowels match too.
            tasks = tasks.alias(
                search_title=Collate('title', 'und-x-icu'),
            ).filter(search_title__icontains=Collate(Value(query), 'und-x-icu'))
        else:
            tasks = tasks.filter(title__icontains=query)

    all_tasks = request.user.tasks.all()
    page = Paginator(tasks, 7).get_page(request.GET.get('page'))
    return render(request, template, {
        'tasks': page,
        'page': page,
        'query': query,
        'status_filter': status_filter,
        'total_count': all_tasks.count(),
        'pending_count': all_tasks.filter(status='pending').count(),
        'completed_count': all_tasks.filter(status='completed').count(),
    })


@login_required
def task_list(request):
    """Render the complete authenticated task list."""
    return _task_list_response(request, request.GET.get('status', ''))


@login_required
@require_POST
def task_toggle(request, pk):
    """Toggle completion for one of the signed-in user's tasks."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = 'completed' if task.status == 'pending' else 'pending'
    task.save(update_fields=['status', 'updated_at'])
    next_url = request.POST.get('next', '')
    if next_url.startswith('/dashboard/') or next_url.startswith('/tasks/'):
        return redirect(next_url)
    return redirect('tasks:dashboard')


@login_required
def task_detail(request, pk):
    """Show a task only when it belongs to the signed-in user."""
    task = get_object_or_404(Task, pk=pk, user=request.user)
    return render(request, 'task_detail.html', {
        'task': task,
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
    })


@login_required
def task_create(request):
    """Create a task owned by the signed-in user."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, _('Task created.'))
            return redirect('tasks:dashboard')
    else:
        form = TaskForm()

    return render(request, 'task_form.html', {
        'form': form,
        'title': _('Create task'),
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
    })


@login_required
def task_update(request, pk):
    """Update one of the signed-in user's tasks; never another user's."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, _('Task updated.'))
            return redirect('tasks:dashboard')
    else:
        form = TaskForm(instance=task)

    return render(request, 'task_form.html', {
        'form': form,
        'task': task,
        'title': _('Edit task'),
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
    })


@login_required
def task_delete(request, pk):
    """Delete one of the signed-in user's tasks; never another user's."""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        messages.success(request, _('Task deleted.'))
        return redirect('tasks:dashboard')

    return render(request, 'task_confirm_delete.html', {
        'task': task,
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
    })
