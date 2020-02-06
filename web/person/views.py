from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin

from audit.mixins import AuditFormMixin
from .models import Address, Company


class AddressCreateView(AuditFormMixin, CreateView):
    model = Address
    fields = ['street', 'street_number', 'unit', 'city_region', 'zip_code', 'address_type', 'city', 'state', 'country']


class AddressDeleteView(DeleteView):
    model = Address
    context_object_name = 'address'
    success_url = reverse_lazy('person:address-list')


class AddressDetailView(LoginRequiredMixin, DetailView):
    model = Address
    context_object_name = 'address'


class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    context_object_name = 'addresses'


class AddressUpdateView(AuditFormMixin, UpdateView):
    model = Address
    fields = ['street']


class CompanyCreateView(AuditFormMixin, CreateView):
    model = Company
    fields = ['name', 'legal_name', 'legal_type', 'cpf_cnpj',  'logo']


class CompanyDeleteView(DeleteView):
    model = Company
    context_object_name = 'company'
    success_url = reverse_lazy('person:company-list')


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    context_object_name = 'company'


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = 'companies'


class CompanyUpdateView(AuditFormMixin, UpdateView):
    model = Company
    fields = ['name', 'legal_name', 'legal_type', 'cpf_cnpj',  'logo']


