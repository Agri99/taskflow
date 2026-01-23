from django.views.generic import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect

from .models import Comment
from tasks.models import Task


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'comments/comment_form.html'

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
    template_name = 'comments/comment_confirm_delete.html'

    def get_queryset(self):
        # Allow deletion when the current user is either the comment author or the owner of the parent task.
        return Comment.objects.deletable_by(self.request.user)

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
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete(by_user=request.user)
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy(
            'tasks:task-detail',
            kwargs={'pk': self.object.task.pk}
            )

class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    fields = ['content']
    template_name = 'comments/comment_form.html'

    def get_queryset(self):
        # Author only editing.
        return Comment.objects.editable_by(self.request.user)
    
    def get_object(self):
        # Enforce author ownership, correct task relationship and 404 on any violation
        comment = get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk'],
            task_id=self.kwargs['task_id'],
        )

        return comment
    
    def form_valid(self, form):
        # The super().form_valid will set self.object to the updated object
        response = super().form_valid(form)
        # Mark edited once only
        self.object.mark_edited()
        self.object.save(update_fields=['edited_at'])
        return response
    
    def get_success_url(self):
        return reverse_lazy(
            'tasks:task-detail',
            kwargs={'pk': self.object.task.pk},
        )