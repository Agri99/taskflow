from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Task

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'status', 'priority', 'due_date']
    template_name = 'task_form.html'
    success_url = reverse_lazy('tasks:task-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user # Add user info
        return super().form_valid(form) # Save and Redirect into success_url
    
class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'status', 'priority', 'due_date']    
    template_name = 'task_form.html'
    success_url = reverse_lazy('tasks:task-list')

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user) # Visiblity and Ownership
    
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_confirm_delete.html'
    success_url = reverse_lazy('tasks:task-list')

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)
    
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_detail.html'
    context_object_name = 'task'

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # Get the original Context (contains the task object as 'task')

        # Attach related comment
        context['comments'] = self.object.comments.select_related('author').order_by('-created_at')
        return context