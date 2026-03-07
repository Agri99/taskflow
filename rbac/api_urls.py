from django.urls import path

from .api_views import AuditListAPIView

app_name = 'rbac-api'

urlpatterns = [
    path('audit/', AuditListAPIView.as_view(), name='audit-api-list'),
]