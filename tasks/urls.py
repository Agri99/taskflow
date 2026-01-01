from django.urls import path
from .views import TaskListView

app_name = 'tasks'

urlpatterns = [
    path('/tasks/', TaskListView.as_view(), name='task-list')
]
