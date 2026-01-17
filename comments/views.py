from django.views.generic import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q

from .models import Comment
from tasks.models import Task


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'comment_form.html'

    def form_valid(self, form):
        # Use 404 for any visibility/ownership mismatch
        # to avoid leaking whether the task exists to unauthorized users
        task = get_object_or_404(
            Task,
            pk=self.kwargs['task_id']
        )

        '''
        If the tasks not to be commentable by others.

        if task.owner != self.request.user:
            raise Http404
        '''

        form.instance.author = self.request.user
        form.instance.task = task
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks:task-detail', kwargs={'pk': self.object.task.pk})
    
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_queryset(self):
        # Allow deletion when the current user is either the comment author or the owner of the parent task.
        return Comment.objects.filter(
            Q(author=self.request.user) | Q(task__owner=self.request.user)
            ) # Q is used to express the OR cleanly

    def get_object(self):
        # Use the restricted queryset so that unauthorized looksup return 404
        comment = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk'],
            task_id=self.kwargs['task_id'],
            )

        # Extra safety, ensure model-level helper agrees
        if not comment.can_be_deleted_by(self.request.user):
            raise Http404
        
        return comment
    
    def get_success_url(self):
        return reverse_lazy('tasks:task-detail', kwargs={'pk': self.object.task.pk})