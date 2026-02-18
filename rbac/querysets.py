from organizations.querysets import OrgScopedQuerySet


class AuditEntryQuerySet(OrgScopedQuerySet):
    def for_user(self, user):
        return super().for_user(user)
    
    def for_organization(self, organization):
        return self.filter(organization=organization)