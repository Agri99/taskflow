from django.urls import path
from .views import CommentCreateView, CommentDeleteView


app_name = 'comments'

urlpatterns = [
    path('add/<int:task_id>/', CommentCreateView.as_view(), name='comment-add'),
    path('delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
]
