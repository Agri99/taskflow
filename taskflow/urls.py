from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('rbac/', include('rbac.urls', namespace='rbac')),
    path('admin/', admin.site.urls),
]