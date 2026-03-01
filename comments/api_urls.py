from django.urls import path
from .api_views import CommentListCreateAPIViews, CommentRetrieveUpdateDestroyAPIView

app_name = 'comments-api'

urlpatterns = [
    path('', CommentListCreateAPIViews.as_view(), name='comment-api-list'),
    path('<int:pk>/', CommentRetrieveUpdateDestroyAPIView.as_view(), name='comment-api-detail')
]