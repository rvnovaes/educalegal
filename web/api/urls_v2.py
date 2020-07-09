from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from django.urls import path, include

from .views_v2 import (
    PlanViewSet,
    DocumentViewSet,
    InterviewViewSet,
    # TenantDocumentViewSet,
    # TenantInterviewViewSet,
    # TenantSchoolViewSet,
    # TenantViewSet,
    TenantPlanView,
    # TenantGedDataViewSet
)

from .docusign_helpers import docusign_webhook_listener

API_TITLE = "Educa Legal API V2"
API_DESCRIPTION = (
    "API para Educa Legal Versão 2 - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("plans/", PlanViewSet.as_view({"get": "list"})),
    path("plans/<int:pk>", PlanViewSet.as_view({"get": "retrieve"})),
    path("documents/", DocumentViewSet.as_view({"post": "create", "patch": "partial_update", "get": "list"})),
    path("documents/<int:pk>", DocumentViewSet.as_view({"get": "retrieve"})),
    path("interviews/", InterviewViewSet.as_view({"get": "list"})),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    # path("tenants/", TenantViewSet.as_view({"get": "list"})),
    # path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/plan/", TenantPlanView.as_view()),
    # path("tenants/<int:pk>/documents/", TenantDocumentViewSet.as_view({"get": "list"})),
    # path("tenants/<int:pk>/interviews/", TenantInterviewViewSet.as_view({"get": "list"})),
    # path("tenants/<int:pk>/schools/", TenantSchoolViewSet.as_view({"get": "list"})),
    # path("tenants/<int:pk>/schools/<int:spk>", TenantSchoolViewSet.as_view({"get": "retrieve"})),
    # path("tenants/<int:pk>/ged/", TenantGedDataViewSet.as_view({"get": "retrieve"})),
    path("docusign/webhook", docusign_webhook_listener),
    path("schema/", schema_view),
    # path("docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    # path("rest-auth/", include("rest_auth.urls")),
    # path("rest-auth/registration/", include('rest_auth.registration.urls')),
]
