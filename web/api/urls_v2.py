from django.urls import path, include
from django.conf.urls import url
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path

from .views_v2 import (
    InterviewViewSet,
    PlanViewSet,
    TenantViewSet,
    create_tenant,
    DocumentViewSet,
    DocumentDownloadViewSet,
    DocumentCloudDownloadViewSet,
    DocumentTypesViewSet,
    SchoolViewSet,
    SchoolUnitViewSet,
    TenantGedDataViewSet,
    UserView,
    WitnessViewSet,
    dashboard_data,
    recover_password,
    reset_password,
    validate_document,
    generate_document,
    send_email,
    send_to_esignature
)

from api.third_party.clicksign_helpers import webhook_listener
from api.third_party.docusign_helpers import docusign_webhook_listener

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

public_endpoints = [
    path("interviews/", InterviewViewSet.as_view({"get": "list"})),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("interviews/document_types/", DocumentTypesViewSet.as_view({"get": "list"})),
    path("plans/", PlanViewSet.as_view({"get": "list"})),
    path("plans/<int:pk>", PlanViewSet.as_view({"get": "retrieve"})),
    path("tenants/", TenantViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/ged_data", TenantGedDataViewSet.as_view({"get": "retrieve"})),
    path("documents/", DocumentViewSet.as_view({"post": "create", "get": "list"})),
    path("documents/<str:identifier>",
         DocumentViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("documents/<str:identifier>/download/",
         DocumentDownloadViewSet.as_view({"get": "retrieve", "delete": "destroy"})),
    path("documents/<str:identifier>/cloud_download/", DocumentCloudDownloadViewSet.as_view({"get": "retrieve"})),
    path("documents/validate/<int:interview_id>", validate_document),
    path("documents/generate/<int:interview_id>", generate_document),
    path("documents/send_email/", send_email),
    path("documents/send_to_esignature/", send_to_esignature),
    path("schools/", SchoolViewSet.as_view({"post": "create", "get": "list"})),
    path("schools/<int:pk>",
         SchoolViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("schools/<int:spk>/school_units", SchoolUnitViewSet.as_view({"post": "create", "get": "list"})),
    path("schools/<int:spk>/school_units/<int:pk>",
         SchoolUnitViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("schools/<int:spk>/witnesses", WitnessViewSet.as_view({"post": "create", "get": "list"})),
    path("schools/<int:spk>/witnesses/<int:pk>",
         WitnessViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
]

# Apenas as URLS acima (public_endpoints) serao adicionadas ao swagger
# A segunda lista de URLS (private_enpoints) esta disponivel mas nao e visualizada no swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Educa Legal API",
        default_version="V2",
        description="API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas",
        terms_of_service="https://www.educalegal.com.br/politica-de-privacidade/",
        contact=openapi.Contact(email="sistemas@educalegal.com.br"),
        license=openapi.License(name="Proprietária. Todos os direitos reservados."),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=public_endpoints)

private_endpoints = [
    path("create_tenant/", create_tenant),
    path("dashboard/", dashboard_data),
    path("recover_password/", recover_password),
    path("reset_password/", reset_password),
    path("users/", UserView.as_view(), name="users"),
    path("clicksign/webhook", webhook_listener),
    path("docusign/webhook", docusign_webhook_listener),
    path("token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("token_refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path("schema/", schema_view),
    # Como existe v1/api-auth com o mesmo include, ele emite esse warning
    # URL namespace 'rest_framework' isn't unique. You may not be able to reverse all URLs in this namespace
    path("api-auth/", include("rest_framework.urls")),
    url(
        r"^docs/swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^docs/swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    url(
        r"^docs/redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]

urlpatterns = public_endpoints + private_endpoints
