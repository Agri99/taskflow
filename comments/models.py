from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from tasks.models import Task
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

    objects = CommentManager()                  # Default Manager: active only
    all_objects = CommentQuerySet.as_manager()  # Access including deleted

    def can_be_deleted_by(self, user):
        # Only author and task owner who can delete
        if not user or not user.is_authenticated:
            return False
        
        return user == self.author or user == self.task.owner
    
    def can_be_edited_by(self, user):
        # Author only
        if not user or not user.is_authenticated:
            return False
        
        return user == self.author
    
    def soft_delete(self, *, by_user):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

    def __str__(self):
        return f'Comment by {self.author}'