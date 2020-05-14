import datetime

from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from tenant.models import Tenant
from document.models import Document

from .models import Plan


class PlanDetailView(LoginRequiredMixin, DetailView):
    model = Plan
    context_object_name = "plan"

    def get_context_data(self, *, object_list=None, **kwargs):
        today = datetime.datetime.today()

        tenant = Tenant.objects.get(pk=self.request.user.tenant.pk)
        total_document_count = Document.objects.filter(tenant=tenant).count()
        document_count_current_month = Document.objects.filter(tenant=tenant,
                                                               created_date__month=today.month,
                                                               created_date__year=today.year).count()
        context = super().get_context_data(**kwargs)
        context['total_document_count'] = total_document_count
        context['document_count_current_month'] = document_count_current_month

        return context
