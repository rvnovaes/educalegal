from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from django.urls import include, path
from .views import SchoolViewSet
from .views import TenantGEDViewSet, TenantSchoolsAPIViewList

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("tenant/ged/", TenantGEDViewSet.as_view({"get": "list"})),
    path("tenant/ged/<int:pk>", TenantGEDViewSet.as_view({"get": "retrieve"})),
    path("tenant/<int:pk>/school/", TenantSchoolsAPIViewList.as_view()),
    path("school/", SchoolViewSet.as_view({"get": "list"})),
    path("school/<int:pk>", SchoolViewSet.as_view({"get": "retrieve"})),
    path("schema/", schema_view),
    path("docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path("v1/rest-auth/", include("rest_auth.urls")),
    # path('v1/rest-auth/registration/', include('rest_auth.registration.urls')),
]
