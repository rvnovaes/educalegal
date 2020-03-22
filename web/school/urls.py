from django.urls import path
from .views import (
    SchoolCreateView,
    SchoolDetailView,
    SchoolDeleteView,
    SchoolListView,
    SchoolUpdateView,
    SchoolUnitCreateView,
    SchoolUnitDetailView,
    SchoolUnitDeleteView,
    SchoolUnitUpdateView,
)

app_name = "school"


urlpatterns = [
    path("school/", SchoolListView.as_view(), name="school-list"),
    path("school/<int:pk>", SchoolDetailView.as_view(), name="school-detail"),
    path("school/create/", SchoolCreateView.as_view(), name="school-create"),
    path("school/update/<int:pk>", SchoolUpdateView.as_view(), name="school-update"),
    path("school/delete/<int:pk>", SchoolDeleteView.as_view(), name="school-delete"),
    path(
        "school/<int:school_id>/school-unit/<int:pk>",
        SchoolUnitDetailView.as_view(),
        name="school-unit-detail",
    ),
    path(
        "school/<int:school_id>/school-unit/create/",
        SchoolUnitCreateView.as_view(),
        name="school-unit-create",
    ),
    path(
        "school/<int:school_id>/school-unit/update/<int:pk>",
        SchoolUnitUpdateView.as_view(),
        name="school-unit-update",
    ),
    path(
        "school/<int:school_id>/school-unit/delete/<int:pk>",
        SchoolUnitDeleteView.as_view(),
        name="school-unit-delete",
    ),
]
