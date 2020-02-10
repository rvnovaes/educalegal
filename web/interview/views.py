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
        uuid = self.request.user.tenant.unique_id
        for item in context['object_list']:
            item.interview_url_with_uuid = item.base_url + '&tid=' + str(uuid) + '&new_session=1'
            print(item.interview_url_with_uuid)
        return context
