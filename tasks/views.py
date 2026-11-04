"""
Views for Cloud Task Manager - authentication flow.

Personal (dashboard) pages are protected with Django's ``login_required``
decorator, so authentication is enforced server-side through the session.
"""
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as lazy_

from .forms import SignUpForm, TaskForm
from .models import Task


def home(request):
    """Public landing page with basic project information."""
    context = {
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
        'features': [
            'User registration and login (session based)',
            'Task management (coming soon)',
            'Cloud deployment',
        ]
    }
    return render(request, 'home.html', context)


def language_settings(request):
    """Simple settings page with the Vietnamese/English language choice.

    Available to anonymous visitors too, so login/register users can switch
    languages. The choice itself is persisted by Django's ``set_language``
    view through the ``LANGUAGE_COOKIE_NAME`` cookie.
    """
    return render(request, 'settings.html', {
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
    })


def health_check(request):
    """Health check endpoint for monitoring. Public, no authentication."""
    return JsonResponse({
        'status': 'ok',
        'service': 'cloud-task-manager',
        'version': '1.1.0-auth'
    })


def register(request):
    """Create a new account, then log the new user in."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Account created. You are now signed in.'))
            return redirect('tasks:dashboard')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    """Personal area: only the signed-in user's tasks are listed.

    The optional ``?status=incomplete|completed`` query parameter filters
    against ``Task.STATUS_CHOICES``. Any other value is ignored and falls
    back to showing all tasks, so invalid input never crashes the page.
    """
    all_tasks = request.user.tasks.all()
    status_filter = request.GET.get('status', '')
    status_map = {'incomplete': 'pending', 'completed': 'completed'}
    # Preserve the original dashboard filter URLs for existing links.
    if status_filter in status_map:
        return _task_list_response(request, status_filter, template='task_list.html')

    today = timezone.localdate()
    soon = today + timedelta(days=6)
    pending = all_tasks.filter(status='pending')
    due_soon = pending.filter(due_date__gte=today, due_date__lte=soon).order_by('due_date', 'created_at')
    priority = list(pending.order_by(F('due_date').asc(nulls_last=True), '-created_at')[:5])
    if len(priority) < 5:
        priority.extend(all_tasks.filter(status='completed').order_by('-updated_at')[:5 - len(priority)])

    context = {
        'project_name': 'Cloud Task Manager',
        'version': '1.1.0-auth',
        'tasks': all_tasks,
        'status_filter': status_filter,
        'pending_count': pending.count(),
        'completed_count': all_tasks.filter(status='completed').count(),
        'due_soon_count': due_soon.count(),
        'due_soon': due_soon[:4],
        'priority_tasks': priority,
        'today': today,
    }
    return render(request, 'dashboard.html', context)


def _task_list_response(request, status_filter='', template='task_list.html'):
    tasks = request.user.tasks.all()
    status_map = {'incomplete': 'pending', 'completed': 'completed'}
    if status_filter in status_map:
        tasks = tasks.filter(status=status_map[status_filter])
    else:
        status_filter = ''
    query = request.GET.get('q', '').strip()[:100]
    if query:
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
    return _task_list_response(request, request.GET.get('status', ''))


@login_required
@require_POST
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = 'completed' if task.status == 'pending' else 'pending'
    task.save(update_fields=['status', 'updated_at'])
    next_url = request.POST.get('next', '')
    # Only local task screens are accepted as return destinations.
    if next_url.startswith('/dashboard/') or next_url.startswith('/tasks/'):
        return redirect(next_url)
    return redirect('tasks:task_list')


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
