from django.urls import path

from .util import send_email, redirect_send_to_esignature
from .views import (
    DocumentListView,
    DocumentDetailView,
    BulkDocumentGenerationListView,
    BulkDocumentGenerationDetailView,
    ValidateCSVFile,
    generate_bulk_documents,
    bulk_generation_progress,
)

app_name = "document"


urlpatterns = [
    path("document/", DocumentListView.as_view(), name="document-list"),
    path("document/<int:pk>", DocumentDetailView.as_view(), name="document-detail"),
    path("document/<str:doc_uuid>", DocumentDetailView.as_view(), name="document-detail"),
    path("bulk_document_generation/", BulkDocumentGenerationListView.as_view(), name="bulk-document-generation-list"),

    path("bulk_document_generation/<int:bulk_document_generation_id>", BulkDocumentGenerationDetailView.as_view(),
         name="bulk-document-generation-detail"),

    path("bulk_document_generation/validate/<int:interview_id>", ValidateCSVFile.as_view(),
         name="bulk-document-generation-validate-generate"),
    path("bulk_document_generation/generate/<int:bulk_document_generation_id>", generate_bulk_documents,
         name="bulk-document-generation-result"),
    path("bulk_document_generation/generate/progress/<int:bulk_document_generation_id>", bulk_generation_progress,
         name="bulk-document-generation-progress"),
    path("send_email/<str:doc_uuid>", send_email, name="send-email"),
    path("send_to_esignature/<str:doc_uuid>", redirect_send_to_esignature, name="send-to-esignature"),
]
