from django.urls import path

from .views import AuditLogView
from .api_views import AuditListAPIView

app_name = 'rbac'

urlpatterns = [
    path('audit/', AuditLogView.as_view(), name='audit-log'),
    path('api/audit/', AuditListAPIView.as_view(), name='audit-api-list'),
]
