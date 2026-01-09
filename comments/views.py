from django.views.generic import CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

from .models import Comment
from tasks.models import Task


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']
    template_name = 'comment_form.html'

    def form_valid(self, form):
        task = get_object_or_404(
            Task,
            pk=self.kwargs['task_id'],
            owner=self.request.user
        )

        form.instance.author = self.request.user
        form.instance.task = task
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tasks:task-detail', kwargs={'pk': self.object.task.pk})
    
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'comment_confirm_delete.html'

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('tasks:task-detail', kwargs={'pk': self.objects.task.pk})
    