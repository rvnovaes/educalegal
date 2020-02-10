from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Interview


class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    context_object_name = "interviews"

    def get_queryset(self):
        return Interview.objects.filter(tenants=self.request.user.tenant_id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tid = self.request.user.tenant.id
        for item in context['object_list']:
            item.interview_with_tid = item.base_url + '&tid=' + str(tid) + '&new_session=1'
            print(item.interview_with_tid)
        return context
