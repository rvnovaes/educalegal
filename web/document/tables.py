import django_tables2 as tables
from django_tables2.utils import A
from .models import Document


class DocumentTable(tables.Table):
    interview = tables.LinkColumn("document:document-detail", args=[A("pk")])
    ged_link = tables.TemplateColumn(template_name="document/ir_button.html", verbose_name="Link")
    created_date = tables.DateTimeColumn(format='d/m/Y H:i')
    altered_date = tables.DateTimeColumn(format='d/m/Y H:i')

    class Meta:
        model = Document
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "interview",
            "school",
            "created_date",
            "altered_date",
            "status",
            "signing_provider",
            "ged_link"
        )
