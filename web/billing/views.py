from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Plan


class PlanDetailView(LoginRequiredMixin, DetailView):
    model = Plan
    context_object_name = "plan"
