from django.core.exceptions import PermissionDenied

from rbac.models import AuditEntry
from rbac.services import user_has_perm


def _require_audit_view(user):
    if not user_has_perm(user, 'rbac.view_auditentry'):
        raise PermissionDenied("You do not have permission to view audit logs.")

def audit_for_user(user, requester):
    # Return audit entries performed by a spesific user.
    _require_audit_view(requester)

    if not user or user.is_anonymous:
        return AuditEntry.objects.none()
    
    return AuditEntry.objects.filter(actor=user).order_by('-timestamp')

def audit_for_object(obj, requester):
    # Return audit entries related to a spesific object.
    _require_audit_view(requester)

    return AuditEntry.objects.filter(
        target_content_type__model=obj._meta.model_name,
        target_object_id=obj.pk,
    ).order_by('-timestamp')

def audit_by_action(action, requester):
    # Return audit entries filtered by action type.
    _require_audit_view(requester)

    return AuditEntry.objects.filter(action=action).order_by('-timestamp')