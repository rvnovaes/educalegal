from django.shortcuts import render
from django.views.generic.edit import CreateView
from audit.mixins import AuditFormMixin

from .models import Tenant


class TenantCreateView(AuditFormMixin, CreateView):
    model = Tenant
    fields = ['name']
