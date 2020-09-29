import datetime

from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.authtoken.models import Token
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView

from tenant.models import Tenant
from document.models import Document, DocumentStatus

from .models import Interview
from .tables import InterviewTable
from .filters import InterviewFilter


def reached_document_limit(tenant_id):
    today = datetime.datetime.today()

    # verifica se atingiu o limite de documentos
    tenant = Tenant.objects.get(pk=tenant_id)
    document_count = Document.objects.filter(tenant=tenant,
                                             created_date__month=today.month,
                                             created_date__year=today.year).count()
    reached_document_limit = False
    if tenant.plan.document_limit:
        if document_count >= tenant.plan.document_limit:
            reached_document_limit = True

    return reached_document_limit, tenant.plan.document_limit


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
