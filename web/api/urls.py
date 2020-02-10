from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.urls import path
from .views import SchoolViewSet
from .views import TenantViewSet, TenantSchoolsAPIViewList

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("tenant/", TenantViewSet.as_view({'get': 'list'})),
    path("tenant/<int:pk>", TenantViewSet.as_view({'get': 'retrieve'})),
    path("tenant/<int:pk>/school", TenantSchoolsAPIViewList.as_view()),
    path("school/", SchoolViewSet.as_view({'get': 'list'})),
    path("school/<int:pk>", SchoolViewSet.as_view({'get': 'retrieve'})),
    path("schema", schema_view),
    path("docs", include_docs_urls(API_TITLE)),
]
