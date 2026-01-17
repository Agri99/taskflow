from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('api/', include("comments.urls", namespace="comments")),
    path('', include('tasks.urls')),
    path('admin/', admin.site.urls),
]
