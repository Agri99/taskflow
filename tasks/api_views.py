from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializers


class TaskListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializers

    def get_queryset(self):
        return Task.objects.for_user(self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(
            owner = self.request.user,
            organization = self.request.user.org_profile.organization,
        )