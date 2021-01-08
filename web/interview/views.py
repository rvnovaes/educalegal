
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.authtoken.models import Token
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView

from document.models import DocumentStatus
from document.views import reached_document_limit

from .models import Interview
from .tables import InterviewTable
from .filters import InterviewFilter


class InterviewListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    template_name = "interview/interview_list.html"
    model = Interview
    context_object_name = "interviews"
    table_class = InterviewTable
    filterset_class = InterviewFilter

    def get_queryset(self):
        return Interview.objects.filter(tenants=self.request.user.tenant_id)

    def get_context_data(self, *, object_list=None, **kwargs):
        # https://stackoverflow.com/questions/27064206/django-check-if-a-related-object-exists-error-relatedobjectdoesnotexist
        # Creates a token for the user if he does not already have one
        if not hasattr(self.request.user, "auth_token"):
            token = Token()
            token.user = self.request.user
            token.save()

        context = super().get_context_data(**kwargs)

        reached_limit, document_limit = reached_document_limit(self.request.user.tenant_id)
        if reached_limit:
            context['document_limit'] = document_limit

        context['reached_document_limit'] = reached_limit
        context['document_status'] = DocumentStatus.RASCUNHO.value
        return context
