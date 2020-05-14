from django.urls import path
from .views import (
    bulk_interview
)

app_name = "bulk_interview"

urlpatterns = [
    path("bulk_interview/<int:interview_id>", bulk_interview, name="bulk_interview"),
]

