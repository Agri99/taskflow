from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Comment
from .serializers import CommentSerializer
from tasks.models import Task


class CommentListCreateAPIViews(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_task(self):
        if not hasattr(self, '_task'):
            self._task = get_object_or_404(
            Task.objects.for_user(self.request.user),
            pk=self.kwargs['task_id']
            )
        return self._task
    
    def get_queryset(self):
        return Comment.objects.for_user(self.request.user).filter(
            task=self.get_task()
        )
    
    def create(self, request, *args, **kwargs):
        task = self.get_task()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = Comment.create_with_audit(
            task = task,
            author = request.user,
            content = serializer.validated_data['content']
        )
        return Response(
            self.get_serializer(comment).data,
            status = status.HTTP_201_CREATED
        )
    

class CommentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.for_user(self.request.user).active()
    
    def perform_update(self, serializer):
        new_content = serializer.validated_data['content']
        serializer.instance.apply_edit(
            new_content = new_content,
            by_user = self.request.user
        )
        serializer.instance.mark_edited()
        serializer.instance.save(update_fields=['edited_at'])
    
    def perform_destroy(self, instance):
        instance.soft_delete(by_user=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)