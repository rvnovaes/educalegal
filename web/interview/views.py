from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.authtoken.models import Token


from .models import Interview


class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    context_object_name = "interviews"

    def get_queryset(self):
        return Interview.objects.filter(tenants=self.request.user.tenant_id)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tid = self.request.user.tenant.id
        # https://stackoverflow.com/questions/27064206/django-check-if-a-related-object-exists-error-relatedobjectdoesnotexist
        # Creates a token for the user if he does not already have one
        if not hasattr(self.request.user, 'auth_token'):
            token = Token()
            token.user = self.request.user
            token.save()
        token = self.request.user.auth_token.key
        for obj in context['object_list']:
            if obj.is_generic is True:
                obj.interview_final_url = obj.base_url + '&tid=' + str(tid) + '&ut=' + token + '&new_session=1'
            else:
                obj.interview_final_url = obj.base_url + '&new_session=1'
        return context
