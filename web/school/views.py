from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2 import SingleTableView

from tenant.mixins import TenantAwareViewMixin, TenantAwareCreateUpdateMixin
from .models import School
from .tables import SchoolTable


class SchoolCreateView(LoginRequiredMixin, TenantAwareCreateUpdateMixin, CreateView):
    model = School
    fields = [
        "name",
        "legal_name",
        "legal_type",
        "cnpj",
        "logo",
        "phone",
        "site",
        "email",
        "street",
        "street_number",
        "unit",
        "neighborhood",
        "zip",
        "city",
        "state",
        "country",
        "letterhead"
    ]


class SchoolDeleteView(LoginRequiredMixin, TenantAwareViewMixin, DeleteView):
    model = School
    context_object_name = "school"
    success_url = reverse_lazy("school:school-list")


class SchoolDetailView(LoginRequiredMixin, TenantAwareViewMixin, DetailView):
    model = School
    context_object_name = "school"


class SchoolListView(LoginRequiredMixin, TenantAwareViewMixin, SingleTableView):
    model = School
    table_class = SchoolTable
    context_object_name = "schools"


class SchoolUpdateView(LoginRequiredMixin, TenantAwareCreateUpdateMixin, UpdateView):
    model = School
    fields = [
        "name",
        "legal_name",
        "legal_type",
        "cnpj",
        "logo",
        "phone",
        "site",
        "email",
        "street",
        "street_number",
        "unit",
        "neighborhood",
        "zip",
        "city",
        "state",
        "country",
        "letterhead"
    ]
