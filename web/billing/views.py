from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from tenant.mixins import TenantAwareViewMixin

from .models import Plan


class SchoolDetailView(LoginRequiredMixin, TenantAwareViewMixin, DetailView):
    model = Plan
    context_object_name = "school"
