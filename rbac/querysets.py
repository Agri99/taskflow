from django.db import models


class OrgScoopedQuerySet(models.QuerySet):
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

class AuditEntryQuerySet(OrgScoopedQuerySet):
    def for_user(self, user):
        return super().for_user(user)
    
    def for_organization(self, organization):
        return self.filter(organization=organization)