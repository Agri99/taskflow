from django.urls import path
from .views import index


app_name = 'comments'

urlpatterns = [
    path('', index, name='comments')
]
