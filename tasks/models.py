"""
Task models - Foundation only, CRUD implementation in later tasks.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Task(models.Model):
    """Task model for personal task management."""

    # Labels are translated for display; the stored database values
    # ('pending' / 'completed') are never localized.
    STATUS_CHOICES = [
        ('pending', _('Not Completed')),
        ('completed', _('Completed')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
