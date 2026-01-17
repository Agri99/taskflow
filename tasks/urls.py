from django.urls import path, include
from .views import *

app_name = 'tasks'

urlpatterns = [
    path('', TaskListView.as_view(), name='task-list'),
    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='task-edit'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/', include('comments.urls', namespace='comments')),
    ]
