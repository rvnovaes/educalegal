import django_tables2 as tables
from django_tables2.utils import A

from .models import Document


class DocumentTable(tables.Table):
    interview = tables.LinkColumn("document:document-detail", args=[A("pk")])
    ged_link = tables.TemplateColumn(
        template_name="document/ir_button.html", verbose_name="Link"
    )
    created_date = tables.DateTimeColumn(format="d/m/Y H:i")
    altered_date = tables.DateTimeColumn(format="d/m/Y H:i")

    def before_render(self, request):
        if not request.user.tenant.use_esignature:
            self.columns.hide('signing_provider')
        if not request.user.tenant.use_ged:
            self.columns.hide('ged_link')
        if not (request.user.tenant.use_ged or request.user.tenant.use_esignature):
            self.columns.hide('altered_date')

    class Meta:
        model = Document
        order_by = "-created_date"
        template_name = "django_tables2/bootstrap4.html"
        per_page = 20
        fields = (
            "interview",
            "school",
            "created_date",
            "altered_date",
            "status",
            "signing_provider",
            "ged_link",
        )
