from django.urls import path
from .views import (
    PlanDetailView,
)

app_name = "billing"


urlpatterns = [
    path("plan/<int:pk>", PlanDetailView.as_view(), name="plan-details"),
]
