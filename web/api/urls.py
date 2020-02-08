from django.urls import path
from .views import TenantAPIViewList, TenantAPIViewDetail


urlpatterns = [
    path("", TenantAPIViewList.as_view()),
    path("<int:pk>", TenantAPIViewDetail.as_view()),
]
