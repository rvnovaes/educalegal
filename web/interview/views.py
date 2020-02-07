from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Interview


class InterviewListView(ListView):
    model = Interview
    context_object_name = 'interviews'

    def get_queryset(self):
        return Interview.objects.filter(tenant_id=self.request.user.tenant_id)
