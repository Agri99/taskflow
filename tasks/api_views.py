from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Task
from .serializers import TaskSerializer
from .filters import TaskFilter


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
        serializer.save(
            owner = self.request.user,
            organization = self.request.user.org_profile.organization,
        )

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