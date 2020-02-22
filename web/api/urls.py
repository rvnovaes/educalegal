from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from django.urls import path, include
from .views import DocumentCreateView
from .views import InterviewViewSet
from .views import TenantSchoolViewSet
from .views import TenantViewSet, TenantGedDataViewSet, TenantESignatureDataViewSet
from .views import docusign_webhook_listener

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("documents/", DocumentCreateView.as_view()),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("tenants/", TenantViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/schools/", TenantSchoolViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>/schools/<int:spk>", TenantSchoolViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/ged/", TenantGedDataViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/esignature/", TenantESignatureDataViewSet.as_view({"get": "retrieve"})),
    path("docusign/webhook", docusign_webhook_listener),
    path("schema/", schema_view),
    path("docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    # path("rest-auth/", include("rest_auth.urls")),
    # path("rest-auth/registration/", include('rest_auth.registration.urls')),
]
