from rest_framework.schemas import get_schema_view
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


from .views_v2 import (
    InterviewViewSet,
    PlanViewSet,
    TenantViewSet,
    DocumentViewSet,
    DocumentDownloadViewSet,
    DocumentCountViewSet,
    TenantSchoolViewSet,
    TenantSchoolUnitViewSet,
    TenantInterviewViewSet,
    TenantPlanViewSet,
    UserView
)

from .clicksign_helpers import webhook_listener
from .docusign_helpers import docusign_webhook_listener

API_TITLE = "Educa Legal API V2"
API_DESCRIPTION = (
    "API para Educa Legal Versão 2 - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    # Administrative Views
    path("interviews/", InterviewViewSet.as_view({"get": "list"})),
    path("interviews/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("plans/", PlanViewSet.as_view({"get": "list"})),
    path("plans/<int:pk>", PlanViewSet.as_view({"get": "retrieve"})),
    path("tenants/", TenantViewSet.as_view({"get": "list"})),
    path("tenants/<int:pk>", TenantViewSet.as_view({"get": "retrieve"})),
    # Documents Views
    path("documents/", DocumentViewSet.as_view({"post": "create", "get": "list"})),
    path("documents/<str:identifier>", DocumentViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("documents/<str:identifier>/download", DocumentDownloadViewSet.as_view({"get": "retrieve", "delete": "destroy"})),
    path("documents/count", DocumentCountViewSet.as_view({"get": "list"})),
    # Front end views
    path("tenant/schools/", TenantSchoolViewSet.as_view({"post": "create", "get": "list"})),
    path("tenant/schools/<int:pk>", TenantSchoolViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),

    path("tenant/schools/<int:spk>/school_units", TenantSchoolUnitViewSet.as_view({"post": "create", "get": "list"})),
    path("tenant/schools/<int:spk>/school_units/<int:pk>", TenantSchoolUnitViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),

    path("tenant/interviews/", TenantInterviewViewSet.as_view({"get": "list"})),
    # path("tenant/interviews/<int:pk>", TenantInterviewViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    path("tenant/plan/<int:pk>", TenantPlanViewSet.as_view({"get": "retrieve"})),
    # path("tenant/ged_data/", TenantGedDataViewSet.as_view({"post": "create", "get": "list"})),
    # path("tenant/ged_data/<int:pk>", TenantGedDataViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"})),
    # Other
    path("clicksign/webhook", webhook_listener),
    path("user/", UserView.as_view(), name="users"),
    path("docusign/webhook", docusign_webhook_listener),
    path("schema/", schema_view),

    path("token/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("token_refresh/", TokenRefreshView.as_view(), name='token_refresh')

]
