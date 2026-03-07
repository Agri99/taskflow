from django.urls import path, include
from .api_views import TaskListCreateAPIView, TaskRetrieveUpdateDestroyAPIView

app_name = 'tasks-api'

urlpatterns = [
    path('', TaskListCreateAPIView.as_view(), name='task-api-list'),
    path('<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view(), name='task-api-detail'),
    path('<int:task_id>/comments/', include('comments.api_urls', namespace='comments-api')),
]