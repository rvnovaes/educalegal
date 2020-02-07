from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Tenant


class TenantCreateView(LoginRequiredMixin, CreateView):
    model = Tenant
    fields = ['name']
