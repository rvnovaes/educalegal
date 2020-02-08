from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from django_tables2 import SingleTableView

from .models import School
from .tables import SchoolTable


class SchoolCreateView(LoginRequiredMixin, CreateView):
    model = School
    fields = ['name', 'legal_name', 'legal_type', 'cnpj', 'logo', 'street',
              'street_number', 'unit', 'city_region', 'zip_code', 'phone', 'site',
              'email', 'city', 'state', 'country']

    def form_valid(self, form):
        form.instance.tenant_id = self.request.user.tenant_id
        return super().form_valid(form)


class SchoolDeleteView(LoginRequiredMixin, DeleteView):
    model = School
    context_object_name = 'school'
    success_url = reverse_lazy('school:school-list')

    def get_queryset(self):
        return School.objects.filter(tenant_id=self.request.user.tenant_id)


class SchoolDetailView(LoginRequiredMixin, DetailView):
    model = School
    context_object_name = 'school'

    def get_queryset(self):
        return School.objects.filter(tenant_id=self.request.user.tenant_id)


class SchoolListView(LoginRequiredMixin, SingleTableView):
    model = School
    table_class = SchoolTable
    context_object_name = 'schools'

    def get_queryset(self):
        return School.objects.filter(tenant_id=self.request.user.tenant_id)


class SchoolUpdateView(LoginRequiredMixin, UpdateView):
    model = School
    fields = ['name', 'legal_name', 'legal_type', 'cnpj', 'logo', 'street',
              'street_number', 'unit', 'city_region', 'zip_code', 'phone', 'site',
              'email', 'city', 'state', 'country']

    def form_valid(self, form):
        form.instance.tenant_id = self.request.user.tenant_id
        return super().form_valid(form)

