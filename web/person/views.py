from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from audit.mixins import AuditFormMixin


from .models import Company
from .forms import CompanyForm


class CompanyCreate(AuditFormMixin, CreateView):
    model = Company
    fields = ['name', 'legal_name']


class CompanyUpdate(UpdateView):
    model = Company
    fields = ['name', 'legal_name']


# class CompanyDelete(DeleteView):
#     model = Company
#     fields = ['name', 'legal_name']


