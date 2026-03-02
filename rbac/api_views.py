from rest_framework.generics import ListAPIView

from .permissions import HasRBACPermission
from .models import AuditEntry
from .serializers import RBACSerializer


class AuditListAPIView(ListAPIView):
    serializer_class = RBACSerializer

    def get_queryset(self):
        return AuditEntry.objects.for_user(self.request.user)
    
    def get_permissions(self):
        return [HasRBACPermission('rbac.view_auditentry')]