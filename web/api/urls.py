from django.urls import path, include
from django.conf.urls import url
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from drf_yasg import openapi

from .views import (
    DocumentViewSet,
    EnvelopeViewSet,
    ESignatureAppSignerKeyViewSet,
    InterviewViewSet,
    PlanViewSet,
    SignerViewSet,
    TenantDocumentViewSet,
    TenantInterviewViewSet,
    TenantSchoolViewSet,
    TenantViewSet,
    TenantGedDataViewSet
)

from api.third_party.clicksign_helpers import webhook_listener
from api.third_party.docusign_helpers import docusign_webhook_listener

public_endpoints = [
    path("plans/<int:pk>", PlanViewSet.as_view({"get": "retrieve"})),
    path("envelopes/", EnvelopeViewSet.as_view({"post": "create"}), ),
    path("documents/", DocumentViewSet.as_view({"post": "create", "patch": "partial_update"}), ),
    path("documents/<int:pk>", DocumentViewSet.as_view({"get": "retrieve"}), ),
    path("documents/<int:id>/signers/", SignerViewSet.as_view({"post": "create"}), ),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("tenants/", TenantViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/documents/", TenantDocumentViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/interviews/", TenantInterviewViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/schools/", TenantSchoolViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/schools/<int:spk>", TenantSchoolViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/ged/", TenantGedDataViewSet.as_view({"get": "retrieve"})),
    path("esignature-app-signer-keys/<str:email>/<str:name>",
         ESignatureAppSignerKeyViewSet.as_view({"get": "retrieve"})),
    path("esignature-app-signer-keys/", ESignatureAppSignerKeyViewSet.as_view({"post": "create"}), ),
    path("clicksign/webhook", webhook_listener),
    path("docusign/webhook", docusign_webhook_listener)]


# Apenas as URLS acima (public_endpoints) serao adicionadas ao swagger
# A segunda lista de URLS (private_enpoints) esta disponivel mas nao e visualizada no swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Educa Legal API",
        default_version="V1",
        description="API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas",
        terms_of_service="https://www.educalegal.com.br/politica-de-privacidade/",
        contact=openapi.Contact(email="sistemas@educalegal.com.br"),
        license=openapi.License(name="Proprietária. Todos os direitos reservados."),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    patterns=public_endpoints)

private_endpoints = [

    path("schema/", schema_view),

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
