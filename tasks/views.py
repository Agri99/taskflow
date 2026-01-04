from django.views.generic import ListView, CreateView, UpdateView, DeleteView
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
    