from django.urls import path
from .views import (
    DocumentListView,
    DocumentDetailView,
)

app_name = "document"


urlpatterns = [
    path("document/", DocumentListView.as_view(), name="document-list"),
    path("document/<int:pk>", DocumentDetailView.as_view(), name="document-detail"),
]
