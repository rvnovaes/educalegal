from django.urls import path
from .views import (
    bulk_interview_documents,
    BulkInterviewListView,
    ValidateCSVFile,
    generate_bulk_documents,
)

app_name = "bulk_interview"

urlpatterns = [
    path("bulk_interview/", BulkInterviewListView.as_view(), name="bulk_interview-list"),
    path("bulk_interview/<int: bulk_interview_id>", bulk_interview_documents, name="bulk_interview-documents"),
    path("bulk_interview/validate/<int:interview_id>", ValidateCSVFile.as_view(), name="bulk_interview_validate_generate"),
    path("bulk_interview/generate/<int:bulk_interview_id>", generate_bulk_documents, name="bulk_interview_generation_result"),
]

