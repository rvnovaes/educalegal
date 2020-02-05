from django.shortcuts import render
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView

from audit.mixins import AuditFormMixin



from .models import Company


class CompanyDetailView(DetailView):
    model = Company


class CompanyCreate(AuditFormMixin, CreateView):
    model = Company
    fields = ['name', 'legal_name']


class CompanyUpdate(UpdateView):
    model = Company
    fields = ['name', 'legal_name']


# class CompanyDelete(DeleteView):
#     model = Company
#     fields = ['name', 'legal_name']


