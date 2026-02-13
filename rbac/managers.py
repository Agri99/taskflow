from django.db import models
from .querysets import AuditEntryQuerySet, OrgScoopedQuerySet
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class OrgScopedManager(models.Manager):
    """Manager that uses OrgScopedQuerySet and exposes .for_user(user)"""
    def get_queryset(self):
        return OrgScoopedQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def for_organization(self, organization):
        return self.get_queryset().for_organization(organization)

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