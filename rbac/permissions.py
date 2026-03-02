from rest_framework.permissions import BasePermission
from .services import user_has_perm

class HasRBACPermission(BasePermission):
    def __init__(self, perm_codename):
        self.perm_codename = perm_codename

    def has_permission(self, request, view):
        return user_has_perm(request.user, self.perm_codename)