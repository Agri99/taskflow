from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType

from .models import Task
from .serializers import TaskSerializer
from .filters import TaskFilter
from .tasks import notify_org_members_new_task
from rbac.models import AuditEntry


class TaskListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority']
    filterset_class = TaskFilter

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = Task.objects.all()
        else:
            qs = Task.objects.for_user(self.request.user)
        return qs.active().order_by('-created_at')
    
    def perform_create(self, serializer):
        task = serializer.save(
                    owner = self.request.user,
                    organization = self.request.user.org_profile.organization,
                    notification_sent = False
                )
        
        AuditEntry.objects.create(
            actor = self.request.user,
            action = 'create',
            target_content_type = ContentType.objects.get_for_model(Task),
            target_object_id = task.id,
            payload = {'notification': 'pending'},
            organization = self.request.user.org_profile.organization,
        )

        try:
            result = notify_org_members_new_task.delay(task.id)
            result.get(timeout=30) # WAIT up to 30 seconds for result

            task.notification_sent = True # Mark as complete only after success
            task.save()
        except Exception as exc:
            task.delete() # Rollback: delete the task we just created
            raise # Return 500 error to user

class TaskRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = Task.objects.all()
        else:
            qs = Task.objects.for_user(self.request.user)
        return qs.active().order_by('-created_at')
    
    def perform_destroy(self, instance):
        instance.soft_delete(by_user=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)