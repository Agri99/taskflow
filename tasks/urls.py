from django.urls import path, include
from .api_views import TaskListCreateAPIView, TaskRetrieveUpdateDestroyAPIView
from .views import TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView, TaskDetailView

app_name = 'tasks'

urlpatterns = [
    path('', TaskListView.as_view(), name='task-list'),
    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('api/', TaskListCreateAPIView.as_view(), name='task-api-list'),
    path('api/<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view(), name='task-api-detail'),
    path('api/<int:task_id>/comments/', include('comments.api_urls', namespace='comments-api')),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='task-edit'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('<int:task_id>/comments/', include('comments.urls', namespace='comments')),
    ]