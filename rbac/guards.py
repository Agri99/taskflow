from django.core.exceptions import PermissionDenied

from rbac.services import user_has_perm


def require_perm(user, perm_code):
    # Raise PermissionDenied if user lacks RBAC permission.
    if not user_has_perm(user, perm_code):
        raise PermissionDenied(f"Missing permission: {perm_code}")
