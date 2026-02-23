from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer


class TaskListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.for_user(self.request.user).active()
    
    def perform_create(self, serializer):
        serializer.save(
            owner = self.request.user,
            organization = self.request.user.org_profile.organization,
        )

class TaskRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.for_user(self.request.user).active()
    
    def perform_destroy(self, instance):
        instance.soft_delete(by_user=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)