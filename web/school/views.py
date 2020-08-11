from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2 import SingleTableView

from tenant.mixins import TenantAwareViewMixin, TenantAwareCreateUpdateMixin
from .models import School
from .models import SchoolUnit
from .tables import SchoolTable


class SchoolCreateView(LoginRequiredMixin, TenantAwareCreateUpdateMixin, CreateView):
    model = School
    fields = [
        "legal_name",
        "name",
        "legal_nature",
        "cnpj",
        "logo",
        "phone",
        "site",
        "email",
        "zip",
        "street",
        "street_number",
        "unit",
        "neighborhood",
        "city",
        "state",
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
        "legal_name",
        "name",
        "legal_nature",
        "cnpj",
        "logo",
        "phone",
        "site",
        "email",
        "zip",
        "street",
        "street_number",
        "unit",
        "neighborhood",
        "city",
        "state",
    ]


class SchoolUnitCreateView(
    LoginRequiredMixin, TenantAwareCreateUpdateMixin, CreateView
):
    model = SchoolUnit
    fields = ["name"]

    def get_success_url(self):
        return reverse_lazy(
            "school:school-detail", kwargs={"pk": self.kwargs["school_id"]}
        )

    def form_valid(self, form):
        form.instance.school_id = self.kwargs["school_id"]
        return super().form_valid(form)


class SchoolUnitDeleteView(LoginRequiredMixin, TenantAwareViewMixin, DeleteView):
    model = SchoolUnit
    context_object_name = "school_unit"

    def get_success_url(self):
        return reverse_lazy(
            "school:school-detail", kwargs={"pk": self.kwargs["school_id"]}
        )


class SchoolUnitDetailView(LoginRequiredMixin, TenantAwareViewMixin, DetailView):
    model = SchoolUnit
    context_object_name = "school_unit"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(school_id=self.kwargs["school_id"])


class SchoolUnitUpdateView(
    LoginRequiredMixin, TenantAwareCreateUpdateMixin, UpdateView
):
    model = SchoolUnit
    fields = ["name"]

    def form_valid(self, form):
        form.instance.school_id = self.kwargs["school_id"]
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "school:school-detail", kwargs={"pk": self.kwargs["school_id"]}
        )
