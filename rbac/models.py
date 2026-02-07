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
    permissions = models.ManyToManyField('auth.Permission', related_name='rbac_roles', blank=True)

    def __str__(self):
        return self.name
    

class Membership(models.Model):
    """
    Assigns a user to a role (global scope).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='membership')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user} -> {self.role}"
        

class AuditEntryManager(models.Manager):
    def create_entry(self, *, actor, action, target, payload=None, timestamp=None):
        """
        Create an AuditEntry for 'target' (a Django model instance).
        """

        ct = ContentType.objects.get_for_model(target)
        return self.create(
            actor = actor,
            action = action,
            target_content_type = ct,
            target_object_id = target.pk,
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
    