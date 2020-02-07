from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import School


class SchoolCreateView(LoginRequiredMixin, CreateView):
    model = School
    fields = ['name', 'legal_name', 'legal_type', 'cnpj', 'logo', 'units', 'street',
              'street_number', 'unit', 'city_region', 'zip_code', 'phone', 'email',
              'city', 'state', 'country']


class SchoolDeleteView(LoginRequiredMixin, DeleteView):
    model = School
    context_object_name = 'school'
    success_url = reverse_lazy('school:company-list')


class SchoolDetailView(LoginRequiredMixin, DetailView):
    model = School
    context_object_name = 'school'


class SchoolListView(LoginRequiredMixin, ListView):
    model = School
    context_object_name = 'schools'


class SchoolUpdateView(LoginRequiredMixin, UpdateView):
    model = School
    fields = ['name', 'legal_name', 'legal_type', 'cnpj', 'logo', 'units', 'street',
              'street_number', 'unit', 'city_region', 'zip_code', 'phone', 'email',
              'city', 'state', 'country']

