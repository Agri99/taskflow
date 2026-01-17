from django.urls import path
from .views import CommentCreateView, CommentDeleteView


app_name = 'comments'

urlpatterns = [
    path('add/', CommentCreateView.as_view(), name='comment-add'),
    path('tasks/<int:task_id>/comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
]
