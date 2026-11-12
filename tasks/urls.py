"""
URL configuration for tasks app.

Authentication URLs live here so that the whole application keeps a single
namespace and a single, consistent set of paths.
"""
from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health'),
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('settings/', views.language_settings, name='settings'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/avatar/', views.profile_avatar, name='profile_avatar'),
    path('profile/avatar/image/', views.profile_avatar_image, name='profile_avatar_image'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/edit/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),
]
