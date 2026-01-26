from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Task
from .mixins import OwnerRequiredMixin
from comments.models import Comment

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'status', 'priority', 'due_date']
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user # Add user info
        return super().form_valid(form) # Save and Redirect into success_url
    
class TaskUpdateView(OwnerRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'status', 'priority', 'due_date']    
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks:task-list')
    
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task-list')

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Any authenticated user can see tasks
        return Task.objects.all()
    
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        '''
        Only task owner can see tasks
        return Task.objects.filter(owner=self.request.user)
        '''
        # Detail view follows the same visibillity rule as the list
        return Task.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Get the original Context (contains the task object as 'task')

        # Attach related comment
        comments_qs = (Comment.objects.filter(task=self.object).select_related('author', 'task'))
        context['comments'] = [
            {
                'comment': comment,
                'can_edit': comment.can_be_edited_by(self.request.user),
                'can_delete': comment.can_be_deleted_by(self.request.user),
            }
            for comment in comments_qs
        ]
        return context
    
