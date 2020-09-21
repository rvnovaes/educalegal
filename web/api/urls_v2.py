from rest_framework.schemas import get_schema_view
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
    SchoolViewSet,
    SchoolUnitViewSet,
    TenantGedDataViewSet,
    UserView,
    WitnessViewSet,
    dashboard_data,
    recover_password,
    reset_password
)

from api.third_party.clicksign_helpers import webhook_listener
from api.third_party.docusign_helpers import docusign_webhook_listener

API_TITLE = "Educa Legal API V2"
API_DESCRIPTION = (
    "API para Educa Legal Versão 2 - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("interviews/", InterviewViewSet.as_view({"get": "list"})),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("plans/", PlanViewSet.as_view({"get": "list"})),
    path("plans/<int:pk>", PlanViewSet.as_view({"get": "retrieve"})),
    path("tenants/", create_tenant),
    path("tenants/", TenantViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    path("tenants/<int:pk>/ged_data", TenantGedDataViewSet.as_view({"get": "retrieve"})),
    path("documents/", DocumentViewSet.as_view({"post": "create", "get": "list"})),
    path("documents/<str:identifier>", DocumentViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("documents/<str:identifier>/download", DocumentDownloadViewSet.as_view({"get": "retrieve", "delete": "destroy"})),
    path("dashboard/", dashboard_data),
    path("recover_password/", recover_password),
    path("reset_password/", reset_password),
    path("schools/", SchoolViewSet.as_view({"post": "create", "get": "list"})),
    path("schools/<int:pk>", SchoolViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("schools/<int:spk>/school_units", SchoolUnitViewSet.as_view({"post": "create", "get": "list"})),
    path("schools/<int:spk>/school_units/<int:pk>", SchoolUnitViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("schools/<int:spk>/witness", WitnessViewSet.as_view({"post": "create", "get": "list"})),
    path("schools/<int:spk>/witnesses/<int:pk>",
         WitnessViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),

    # path("tenant/interviews/<int:pk>", TenantInterviewViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    # path("tenants/plan/<int:pk>", TenantPlanViewSet.as_view({"get": "retrieve"})),
    # path("tenant/ged_data/", TenantGedDataViewSet.as_view({"post": "create", "get": "list"})),
    # path("tenant/ged_data/<int:pk>", TenantGedDataViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    # Other
    path("clicksign/webhook", webhook_listener),
    path("users/", UserView.as_view(), name="users"),
    path("docusign/webhook", docusign_webhook_listener),
    path("schema/", schema_view),
    path("token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("token_refresh/", TokenRefreshView.as_view(), name='token_refresh')

]
