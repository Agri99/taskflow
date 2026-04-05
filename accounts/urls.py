from django.urls import path
from taskflow.views import index


app_name = 'accounts'

urlpatterns = [
    path('', index, name='accounts')
]
