from django.db import models
from .querysets import AuditEntryQuerySet


class AuditEntryManager(models.Manager):
    def get_queryset(self):
        return AuditEntryQuerySet(self.model, using=self._db)
    
    def for_organization(self, organization):
        return self.get_queryset().for_organization(organization)