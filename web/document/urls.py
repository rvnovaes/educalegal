from django.urls import path
from .views import (
    DocumentListView,
    DocumentDetailView,
    # bulk_interview_documents,
    BulkDocumentGenerationListView,
    ValidateCSVFile,
    generate_bulk_documents,
)

app_name = "document"


urlpatterns = [
    path("document/", DocumentListView.as_view(), name="document-list"),
    path("document/<int:pk>", DocumentDetailView.as_view(), name="document-detail"),
    path("bulk_interview/", BulkDocumentGenerationListView.as_view(), name="bulk_interview-list"),
    # path("bulk_interview/<int: bulk_interview_id>", bulk_interview_documents, name="bulk_interview-documents"),
    path("bulk_interview/validate/<int:interview_id>", ValidateCSVFile.as_view(), name="bulk_interview_validate_generate"),
    path("bulk_interview/generate/<int:bulk_interview_id>", generate_bulk_documents, name="bulk_interview_generation_result"),
]
