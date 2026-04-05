from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from .models import AuditEntry
from .services import user_has_perm


class AuditLogView(LoginRequiredMixin, ListView):
    """
    Display audit logs with filtering capabilities.
    Only accessible to users with view_auditery permission.
    """
    model = AuditEntry
    template_name = 'rbac/audit_log.html'
    context_object_name = 'audit_entries'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        """Check RBAC permission before allowing access"""
        if not user_has_perm(request.user, 'rbac.view_auditentry'):
            raise PermissionDenied('You do not have permission to view audit logs.')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filter audit entries by organization and optional query params"""
        if self.request.user.is_superuser:
            qs = AuditEntry.objects.all()
        else:
            qs = AuditEntry.objects.for_user(self.request.user)

        qs = qs.select_related('actor', 'target_content_type', 'organization')
        qs = qs.order_by('-timestamp')

        # Filter by action type
        action = self.request.GET.get('action')
        if action and action in dict(AuditEntry.ACTION_CHOICES):
            qs = qs.filter(action=action)

        # Filter by actor
        actor_id = self.request.GET.get('actor')
        if actor_id:
            qs = qs.filter(actor_id=actor_id)

        # Filter by target type
        target_type = self.request.GET.get('target_type')
        if target_type:
            qs = qs.filter(target_content_type__model=target_type)

        # Search in payload or actor username
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(actor__username__icontains=search) |
                Q(payload__icontains=search)
            )

        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Pass filter values back to template for form persistence
        context['current_action'] = self.request.GET.get('action', '')
        context['current_actor'] = self.request.GET.get('actor', '')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_target_type'] = self.request.GET.get('target_type', '')

        # Provide action chioces for filter dropdown
        context['action_choices'] = AuditEntry.ACTION_CHOICES

        # Get unique target types for filter dropdown
        from django.contrib.contenttypes.models import ContentType
        context['target_types'] = ContentType.objects.filter(
            id__in = AuditEntry.objects.for_user(self.request.user).values_list('target_content_type', flat=True).distinct()
        )

        # Get all actors for filter dropdown
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context['actors'] = User.objects.filter(
            id__in = AuditEntry.objects.for_user(self.request.user).values_list('actor', flat=True).distinct()
        ).order_by('username')

        return context