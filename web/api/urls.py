from rest_framework.schemas import get_schema_view
from django.urls import path

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

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("plans/<int:pk>", PlanViewSet.as_view({"get": "retrieve"})),
    path("envelopes/", EnvelopeViewSet.as_view({"post": "create"}),),
    path("documents/", DocumentViewSet.as_view({"post": "create", "patch": "partial_update"}),),
    path("documents/<int:pk>", DocumentViewSet.as_view({"get": "retrieve"}),),
    path("documents/<int:id>/signers/", SignerViewSet.as_view({"post": "create"}),),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("tenants/", TenantViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/documents/", TenantDocumentViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/interviews/", TenantInterviewViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/schools/", TenantSchoolViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/schools/<int:spk>", TenantSchoolViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/ged/", TenantGedDataViewSet.as_view({"get": "retrieve"})),
    path("esignature-app-signer-keys/<str:email>", ESignatureAppSignerKeyViewSet.as_view({"get": "retrieve"})),
    path("esignature-app-signer-keys/", ESignatureAppSignerKeyViewSet.as_view({"post": "create"}),),
    path("clicksign/webhook", webhook_listener),
    path("docusign/webhook", docusign_webhook_listener),
    path("schema/", schema_view),
    # path("docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    # path("rest-auth/", include("rest_auth.urls")),
    # path("rest-auth/registration/", include('rest_auth.registration.urls')),
]
