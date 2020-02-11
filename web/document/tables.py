import django_tables2 as tables
from django_tables2.utils import A
from .models import Document


class SchoolTable(tables.Table):
    # name = tables.LinkColumn("school:school-detail", args=[A("pk")])

    class Meta:
        model = Document
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "created_date", "altered_date", "interview")
