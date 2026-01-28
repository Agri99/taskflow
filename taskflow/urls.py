from django.contrib import admin
from django.urls import path, include
from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('admin/', admin.site.urls),
]