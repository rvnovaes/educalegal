import django_tables2 as tables

from .models import Interview
from .columns import InterviewCustomUrlColumn, BulkInterviewColumn


class InterviewTable(tables.Table):
    date_available = tables.DateTimeColumn(format="d/m/Y")
    base_url = InterviewCustomUrlColumn(
        template_name="interview/criar_button.html", verbose_name="Criar", orderable=False
    )

    bulk_interview = BulkInterviewColumn(
        template_name="interview/bulk_button.html", verbose_name="Em lote", orderable=False
    )

    def before_render(self, request):
        if not request.user.tenant.plan.use_bulk_interview:
            self.columns.hide('bulk_interview')

    class Meta:
        model = Interview
        order_by = "name"
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "description", "version", "date_available", "base_url")
