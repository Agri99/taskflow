from django.urls import path
from .api_views import CommentListCreateAPIViews

app_name = 'comments-api'

urlpatterns = [
    path('', CommentListCreateAPIViews.as_view(), name='comment-api-list'),
]