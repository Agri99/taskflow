from django.db import models


class AuditEntryQuerySet(models.QuerySet):
    def for_organization(self, organization):
        return self.filter(organization=organization)