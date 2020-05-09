from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView
from django_tables2.paginators import LazyPaginator

from tenant.mixins import TenantAwareViewMixin
from .models import Document
from .tables import DocumentTable


class DocumentDetailView(LoginRequiredMixin, TenantAwareViewMixin, DetailView):
    model = Document
    context_object_name = "document"


class DocumentListView(LoginRequiredMixin, TenantAwareViewMixin, SingleTableView):
    model = Document
    table_class = DocumentTable
    paginator_class = LazyPaginator
    context_object_name = "documents"