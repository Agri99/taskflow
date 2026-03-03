from rest_framework.generics import ListAPIView

from .permissions import HasRBACPermission
from .models import AuditEntry
from .serializers import AuditEntrySerializer


class AuditListAPIView(ListAPIView):
    serializer_class = AuditEntrySerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = AuditEntry.objects.all()
        else:
            qs = AuditEntry.objects.for_user(self.request.user)
        return qs.order_by('-timestamp')
    
    def get_permissions(self):
        return [HasRBACPermission('rbac.view_auditentry')]