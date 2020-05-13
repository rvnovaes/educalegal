import django_tables2 as tables

from .models import Interview
from .columns import InterviewCustomUrlColumn, BulkInterviewColumn


class InterviewTable(tables.Table):
    date_available = tables.DateTimeColumn(format="d/m/Y")

    class Meta:
        model = Interview
        order_by = "name"
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "description", "version", "date_available", "base_url", "bulk_interview")

    base_url = InterviewCustomUrlColumn(
        template_name="interview/criar_button.html", verbose_name="Criar", orderable=False
    )

    bulk_interview = BulkInterviewColumn(
        template_name="interview/bulk_button.html", verbose_name="Em lote", orderable=False
    )
