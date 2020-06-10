import django_tables2 as tables
from django_tables2.utils import A

from .models import BulkInterview


class BulkInterviewTable(tables.Table):
    bulk_generation = tables.LinkColumn("bulk_interview:bulk_interview-detail", args=[A("pk")])
    created_date = tables.DateTimeColumn(format="d/m/Y H:i")
    documentos = tables.TemplateColumn(
        template_name="bulk_interview/documentos_button.html", verbose_name="Documentos"
    )

    class Meta:
        model = BulkInterview
        order_by = "-created_date"
        template_name = "django_tables2/bootstrap4.html"
        per_page = 20
        fields = (
            "created_date",
            "interview",
            "mongo_db_collection_name",
            "documentos"
        )