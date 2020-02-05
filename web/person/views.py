from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin


from audit.mixins import AuditFormMixin


from .models import Company


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company


class CompanyCreateView(AuditFormMixin, CreateView):
    model = Company
    fields = ['name', 'legal_name']


class CompanyUpdateView(AuditFormMixin, UpdateView):
    model = Company
    fields = ['name', 'legal_name']


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = 'companies'


class CompanyDeleteView(DeleteView):
    model = Company
    success_url = reverse_lazy('person:company-list')


