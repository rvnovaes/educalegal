from django.urls import path
from .views import (
    ValidadeCSVFile,
    bulk_interview
)

app_name = "bulk_interview"

urlpatterns = [
    path("bulk_interview/validate/<int:interview_id>", ValidadeCSVFile.as_view(), name="bulk_interview_validate"),
    path("bulk_interview/<int:interview_id>", bulk_interview, name="bulk_interview"),
]

