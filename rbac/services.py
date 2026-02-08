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

def user_has_perm(user, perm_codename):
    """
    Check if user has a spesific permission via RBAC or is superuser.
    perm_codename format: "app_lable.codename"
    """
    if not user or user.is_anonymous:
        return False
    
    if user.is_superuser:
        return True
    
    return perm_codename in get_user_permissions(user)