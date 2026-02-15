from django.db import models


class OrgScoopedQuerySet(models.QuerySet):
    def for_user(self, user):
        if not user or user.is_anonymous:
            return self.none()
        
        if not hasattr(user, 'org_profile'):
            return self.none()
        
        return self.filter(
            organization=user.org_profile.organization
        )

class OrgScopedManager(models.Manager):
    def get_queryset(self):
        return OrgScoopedQuerySet(self.model, using=self._db)
    
    def for_user(self, user):
        return self.get_queryset().for_user(user)