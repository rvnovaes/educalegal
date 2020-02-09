from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from django.urls import path
from .views import TenantAPIViewList, TenantAPIViewDetail

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("tenant", TenantAPIViewList.as_view()),
    path("tenant/<uuid:unique_id>", TenantAPIViewDetail.as_view()),
    path("schema", schema_view),
    path("docs", include_docs_urls(API_TITLE)),
]
