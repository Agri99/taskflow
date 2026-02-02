from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from typing import TYPE_CHECKING

from tasks.models import Task
from typing import ClassVar
from .managers import CommentQuerySet, CommentManager

User = get_user_model()

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='deleted_comments'
    )
    edited_at = models.DateTimeField(null=True, blank=True)

    objects: ClassVar[CommentManager] = CommentManager()                  # Default Manager: active only
    all_objects = CommentQuerySet.as_manager()  # Access including deleted

    def can_be_deleted_by(self, user):
        if self.is_deleted:
            return False
        
        # Only author and task owner who can delete
        if not user or not user.is_authenticated:
            return False
        
        return user == self.author or user == self.task.owner
    
    def can_be_edited_by(self, user):
        if self.is_deleted:
            return False
        
        # Author only
        if not user or not user.is_authenticated:
            return False
        
        if user != self.author:
            return False
        
        if self.edited_at is not None:
            return False # FIRST_EDIT_ONLY
        
        window = getattr(settings, 'COMMENT_EDIT_WINDOW_MINUTES', None)
        if window is None:
            return True # Unlimited editing if disabled
        
        return timezone.now() <= self.created_at + timedelta(minutes=window)
    
    def mark_edited(self):
        if self.edited_at is None:
            self.edited_at = timezone.now()
    
    @property
    def is_edited(self):
        return (
            self.edited_at is not None
            and not self.is_deleted
            )
    
    def soft_delete(self, *, by_user):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

        try:
            from rbac.models import AuditEntry

            AuditEntry.objects.create_entry(
                actor = by_user,
                action = AuditEntry.ACTION_DELETE,
                target = self,
                payload = {'is_deleted': True},
            )
        except Exception:
            # Test will ensure happy-patch works, and ops can tighten error handling later.
            pass

    def __str__(self):
        return f'Comment by {self.author}'