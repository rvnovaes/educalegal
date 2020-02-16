from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from django.urls import include, path
from .views import DocumentCreateView
from .views import InterviewViewSet
from .views import SchoolViewSet
from .views import TenantGEDViewSet, TenantSchoolsViewList
from .views import docusign_webhook_listener

API_TITLE = "Educa Legal API"
API_DESCRIPTION = (
    "API para Educa Legal - Plataforma Digital de Serviços Jurídicos para Escolas"
)

schema_view = get_schema_view(title=API_TITLE)

urlpatterns = [
    path("document/", DocumentCreateView.as_view()),
    path("interview/<int:pk>", InterviewViewSet.as_view({"get": "retrieve"})),
    path("school/", SchoolViewSet.as_view({"get": "list"})),
    path("school/<int:pk>", SchoolViewSet.as_view({"get": "retrieve"})),
    path("tenant/ged/", TenantGEDViewSet.as_view({"get": "list"})),
    path("tenant/ged/<int:pk>", TenantGEDViewSet.as_view({"get": "retrieve"})),
    path("tenant/<int:pk>/school/", TenantSchoolsViewList.as_view()),
    path("docusign/webhook", docusign_webhook_listener),
    path("schema/", schema_view),
    path("docs/", include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    path("v1/rest-auth/", include("rest_auth.urls")),
    # path('v1/rest-auth/registration/', include('rest_auth.registration.urls')),
]
