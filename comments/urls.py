from django.urls import path
from .views import CommentCreateView, CommentDeleteView, CommentUpdateView


app_name = 'comments'

urlpatterns = [
    path('add/', CommentCreateView.as_view(), name='comment-add'),
    path('<int:pk>/edit/', CommentUpdateView.as_view(), name='comment-edit'),
    path('<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
]
