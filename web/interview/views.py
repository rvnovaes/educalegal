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
        for object in context['object_list']:
            if object.is_generic is True:
                object.interview_final_url = object.base_url + '&tid=' + str(tid) + '&new_session=1'
            else:
                object.interview_final_url = object.base_url + '&new_session=1'
        return context
