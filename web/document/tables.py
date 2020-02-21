import django_tables2 as tables
from django_tables2.utils import A
from .models import Document


class DocumentTable(tables.Table):
    name = tables.LinkColumn("document:document-detail", args=[A("pk")])

    class Meta:
        model = Document
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "school", "created_date", "altered_date", "interview", "status", "signing_provider")
