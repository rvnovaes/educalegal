from django.urls import path
from .views import (
    BillingDetailView,
)

app_name = "billing"


urlpatterns = [
    path("plan/<int:pk>", BillingDetailView.as_view(), name="plan-details"),
]
