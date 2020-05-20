from django.urls import path
from .views import (
    ValidadeCSVFile,
    generate_bulk_documents,
    bulk_interview
)

app_name = "bulk_interview"

urlpatterns = [
    path("bulk_interview/validate/<int:interview_id>", ValidadeCSVFile.as_view(), name="bulk_interview_validate_generate"),
    path("bulk_interview/generate/<int:bulk_generation_id>", generate_bulk_documents, name="bulk_interview_generation_result"),
    path("bulk_interview/<int:interview_id>", bulk_interview, name="bulk_interview"),
]

