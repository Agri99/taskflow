from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone

User = get_user_model()


class Role(models.Model):
    """
    A named role that carries a list of permission strings.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    permissions = models.JSONField(default=list)

    def __str__(self):
        return self.name
    
    def has_perm(self, perm: str) -> bool:
        """
        Return True if role grants 'perm'

        'perm' should be a string like 'comment.delete' or 'task.edit'
        """
        return perm in (self.permissions or [])
    

class Membership(models.Model):
    """
    Maps a user to a role, optionally scoped to a specific object.

    If content_type/object_id are NULL, the membership is global.
    This supports per-Task (or other object) RBAC by using a GenericForeignKey.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='membership')

    # Generic relation to scope membership (null -> global role)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'role', 'content_type', 'object_id'], name='unique_membership')
            ]
    
    def __str__(self):
        scope = f" on {self.content_type}#{self.object_id}' if self.content_type else '(global)"
        return f"{self.user} -> {self.role}{scope}"
        
class AuditEntryManager(models.Manager):
    def create_entry(self, *, actor, action, target, payload=None, timestamp=None):
        """
        Create an AuditEntry for 'target' (a Django model instance).
        """

        ct = ContentType.objects.get_for_model(target)
        obj_id = getattr(target, 'pk', None)
        return self.create(
            actor = actor,
            action = action,
            target_content_type = ct,
            target_object_id = obj_id,
            payload = payload or {},
            timestamp = timestamp or timezone.now()
        )
    
class AuditEntry(models.Model):
    """
    Immutable audit record for important actions.

    Fields:
    - actor: user who performed the action (nullable for system actions)
    - action: short stirng (create/edit/delete)
    - target: GenericForeignKey to the model instance
    - timestamp: when the action occured
    - payload: small JSON diff or metadata (immutable by convention)
    """

    ACTION_CREATE = 'create'
    ACTION_EDIT = 'edit'
    ACTION_DELETE = 'delete'

    ACTION_CHOICES = [
        (ACTION_CREATE, 'create'),
        (ACTION_EDIT, 'edit'),
        (ACTION_DELETE, 'delete'),
    ]

    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')

    timestamp = models.DateTimeField(default=timezone.now(), db_index=True)
    payload = models.JSONField(default=dict, editable=False)

    objects = AuditEntryManager()

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['target_content_type', 'target_object_id'])]    
        
    def __str__(self):
        return f"AuditEntry({self.action}) on {self.target_content_type}#{self.target_object_id} by {self.actor} @ {self.timestamp}"
    