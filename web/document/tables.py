import django_tables2 as tables
from django_tables2.utils import A

from .models import Document, BulkDocumentGeneration, DocumentTaskView


class DocumentTable(tables.Table):
    interview = tables.LinkColumn("document:document-detail", args=[A("pk")])
    ged_link = tables.TemplateColumn(
        template_name="document/download_button.html", verbose_name="Baixar"
    )
    created_date = tables.DateTimeColumn(format="d/m/Y H:i")
    altered_date = tables.DateTimeColumn(format="d/m/Y H:i")

    def before_render(self, request):
        if not request.user.tenant.plan.use_esignature:
            self.columns.hide('signing_provider')
        if not request.user.tenant.plan.use_ged:
            self.columns.hide('ged_link')
        if not (request.user.tenant.plan.use_ged or request.user.tenant.plan.use_esignature):
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
            "submit_to_esignature",
            "status",
            "ged_link",
        )


class BulkDocumentGenerationTable(tables.Table):
    created_date = tables.DateTimeColumn(format="d/m/Y H:i")
    tarefas = tables.TemplateColumn(
        template_name="document/lote_button.html", verbose_name="Lote"
    )

    class Meta:
        model = BulkDocumentGeneration
        order_by = "-created_date"
        template_name = "django_tables2/bootstrap4.html"
        per_page = 20
        fields = (
            "created_date",
            "interview",
            "status",
            "tarefas"
        )


class DocumentTaskViewTable(tables.Table):
    interview = tables.LinkColumn("document:document-detail", args=[A("pk")])
    task_name = tables.TemplateColumn(
        template_name="document/task_name.html", verbose_name="Tipo de Tarefa"
    )
    task_status = tables.TemplateColumn(
        template_name="document/task_status.html", verbose_name="Status de Tarefa"
    )
    ged_link = tables.TemplateColumn(
        template_name="document/download_button.html", verbose_name="Baixar"
    )

    class Meta:
        model = DocumentTaskView
        template_name = "django_tables2/bootstrap4.html"
        per_page = 20
        order_by = "doc_uuid"

        fields = (
            "interview",
            "school",
            "task_done_date",
            "submit_to_esignature",
            "document_status",
            "doc_uuid",
            "task_name",
            "task_status",
            "signing_provider",
            "ged_link",
        )