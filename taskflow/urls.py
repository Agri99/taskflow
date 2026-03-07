from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import index


urlpatterns = [
    # Django views (HTML)
    path('', index, name='index'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('tasks/', include('tasks.urls', namespace='tasks')),
    path('rbac/', include('rbac.urls', namespace='rbac')),
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('tasks/', include('tasks.api_urls', namespace='tasks-api')),
        path('rbac/', include('rbac.api_urls', namespace='rbac-api')),
    ])),
]