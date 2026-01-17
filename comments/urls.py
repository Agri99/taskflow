from django.urls import path
from .views import CommentCreateView, CommentDeleteView, CommentUpdateView


app_name = 'comments'

urlpatterns = [
    path('add/', CommentCreateView.as_view(), name='comment-add'),
    path('<int:task_id>/comments/<int:pk>/edit/', CommentUpdateView.as_view(), name='comment-edit'),
    path('<int:task_id>/comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
]
