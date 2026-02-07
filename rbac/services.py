from django.contrib.auth.models import Permission


def get_user_permissions(user):
    """
    Return a set of permission codenames granted via RBAC roles.
    """

    if not user or user.is_anonymous:
        return set()
    
    perms = set()

    for membership in user.memberships.select_related('role').all():
        role = membership.role
        # role.permissions is a ManyToMany to Permission
        for p in role.permissions.select_related('content_type').all():
            perms.add(f"{p.content_type.app_label}.{p.codename}")
    return perms