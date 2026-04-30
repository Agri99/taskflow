from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from organizations.querysets import OrgScopedManager
from rbac.models import AuditEntry, OrgModel
from rbac.services import user_has_perm

User = get_user_model()


class Task(OrgModel):
    STATUS_CHOICES = [
        ('T', 'todo'),
        ('I', 'in_progress'),
        ('D', 'done'),
    ]
    PRIORITY_CHOICES = [
        ('L', 'low'),
        ('M', 'medium'),
        ('H', 'high'),
    ]
    title = models.CharField(max_length=50)
    notification_sent = models.BooleanField(default=False)
    description = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='T')
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='L')
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='deleted_tasks')

    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name='tasks')

    objects = OrgScopedManager()

    def can_be_deleted_by(self, user):
        if not user or user.is_anonymous:
            return False
        
        if self.owner == user:
            return True
        
        if user_has_perm(user, 'tasks.delete_task'):
            return True
        
        return False

    def soft_delete(self, *, by_user):
        if not self.can_be_deleted_by(by_user):
            raise PermissionDenied('You have no permission to delete this task.')
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by'])

        try:
            AuditEntry.objects.create_entry(
                actor = by_user,
                action = AuditEntry.ACTION_DELETE,
                target = self, 
                payload ={'is_deleted': True}
            )
        except Exception:
            pass

    def __str__(self):
        return self.title