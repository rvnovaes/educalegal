from django.urls import path
from .views import (
    DocumentListView,
    DocumentDetailView,
    BulkDocumentGenerationListView,
    ValidateCSVFile,
    generate_bulk_documents,
    bulk_generation_progress
)

app_name = "document"


urlpatterns = [
    path("document/", DocumentListView.as_view(), name="document-list"),
    path("document/<int:pk>", DocumentDetailView.as_view(), name="document-detail"),
    path("bulk_document_generation/", BulkDocumentGenerationListView.as_view(), name="bulk-document-generation-list"),
    path("bulk_document_generation/<int:bulk_document_generation_id>", DocumentListView.as_view(), name="bulk-document-generation-document-list"),
    path("bulk_document_generation/validate/<int:interview_id>", ValidateCSVFile.as_view(), name="bulk-document-generation-validate-generate"),
    # TODO chamar via ajax
    path("bulk_document_generation/generate/<int:bulk_document_generation_id>", generate_bulk_documents, name="bulk-document-generation-result"),
    path("bulk_document_generation/generate/progress/<int:bulk_document_generation_id>", bulk_generation_progress, name="bulk-document-generation-progress"),
]
