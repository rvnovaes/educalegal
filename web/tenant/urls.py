from django.urls import path
from .views import TenantCreateView

app_name = 'tenant'

urlpatterns = [
    path('create/', TenantCreateView.as_view(), name='tenant-create'),
]