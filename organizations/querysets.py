from django.db import models


class OrgScopedQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_deleted=False)

    """QuerySet helper to scope queries to a user's organization."""
    def for_user(self, user):
        # Return queryset scoped to the user's organization (defensive).
        if not user or getattr(user, 'is_anonymous', True):
            return self.none()
        
        if not hasattr(user, 'org_profile') or user.org_profile is None:
            return self.none()
        
        return self.filter(
            organization=user.org_profile.organization
        )
    
    def for_organization(self, organization):
        """Return queryset filtered to the given organization."""
        if organization is None:
            return self.none()
        return self.filter(organization=organization)

 
class OrgScopedManager(models.Manager):
    """Manager that uses OrgScopedQuerySet and exposes .for_user(user)"""
    def get_queryset(self):
        return OrgScopedQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()

    def for_user(self, user):
        return self.get_queryset().for_user(user)
    
    def for_organization(self, organization):
        return self.get_queryset().for_organization(organization)