from .querysets import AuditEntryQuerySet
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from organizations.querysets import OrgScopedManager


class AuditEntryManager(OrgScopedManager):
    """Manager for AuditEntry: keep create_entry factory + org scoping."""
    def get_queryset(self):
        # Use the AuditEntryQuerySet specificaly (inherits org scoping)
        return AuditEntryQuerySet(self.model, using=self._db)
    
    def create_entry(self, *, actor, action, target, payload=None, timestamp=None):
        """Create an AuditEntry for 'target' (a Django model instance)."""
        ct = ContentType.objects.get_for_model(target)
        org = getattr(target, 'organization', None)
        return self.create(
            actor = actor,
            action = action, 
            target_content_type = ct,
            target_object_id = target.pk,
            payload = payload or {},
            timestamp = timestamp or timezone.now(),
            organization = org
        )