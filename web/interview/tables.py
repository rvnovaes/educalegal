import django_tables2 as tables

from .models import Interview
from .columns import InterviewCustomUrlColumn


class InterviewTable(tables.Table):
    class Meta:
        model = Interview
        order_by = "name"
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "description", "version", "date_available", "base_url")

    base_url = InterviewCustomUrlColumn(
        template_name="interview/criar_button.html", verbose_name="Criar"
    )
