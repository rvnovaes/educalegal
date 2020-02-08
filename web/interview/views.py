from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Interview


class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    context_object_name = "interviews"

    def get_queryset(self):
        return Interview.objects.filter(tenant_id=self.request.user.tenant_id)
