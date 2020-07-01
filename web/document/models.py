from django.db import models
from django.contrib.postgres.fields import JSONField
import uuid

from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School


class BulkDocumentGeneration(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    interview = models.ForeignKey(
        Interview, null=True, on_delete=models.CASCADE, verbose_name="Modelo"
    )
    field_types_dict = JSONField(
        null=False, default=dict, verbose_name="Campos do Modelo"
    )
    required_fields_dict = JSONField(
        null=False, default=dict, verbose_name="Obrigatoriedade dos Campos do Modelo"
    )
    parent_fields_dict = JSONField(
        default=dict, verbose_name="Objeto que contém o campo"
    )
    school_names_set = JSONField(
        null=False, default=dict, verbose_name="Conjunto de Nomes de Escola"
    )
    school_units_names_set = JSONField(
        null=False, default=dict, verbose_name="Conjunto de Nomes de Unidades Escolares"
    )
    mongo_db_collection_name = models.CharField(
        max_length=1024, null=False, verbose_name="Coleção de Documentos no Mongo"
    )
    status = models.CharField(max_length=256, default="", verbose_name="Status")


class Document(TenantAwareModel):
    name = models.CharField(max_length=512, verbose_name="Nome")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    signing_provider = models.CharField(
        max_length=256, default="", verbose_name="Provedor"
    )
    envelope_id = models.CharField(
        max_length=256, default="", verbose_name="Id do Envelope"
    )
    status = models.CharField(max_length=256, default="", verbose_name="Status")
    ged_id = models.CharField(
        max_length=128, default="", verbose_name="ID do Documento no GED"
    )
    ged_link = models.CharField(max_length=256, default="", verbose_name="Link")
    ged_uuid = models.CharField(
        max_length=256,
        default="",
        help_text="UUID do documento. UUID = Universally Unique ID.",
        verbose_name="UUID",
    )
    description = models.TextField(default="", verbose_name="Descrição")
    interview = models.ForeignKey(
        Interview, null=True, on_delete=models.CASCADE, verbose_name="Modelo"
    )
    school = models.ForeignKey(
        School, null=True, on_delete=models.CASCADE, verbose_name="Escola"
    )
    related_documents = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )
    document_data = JSONField(null=True, verbose_name="Dados do Documento")

    bulk_generation = models.ForeignKey(
        BulkDocumentGeneration, null=True, on_delete=models.CASCADE, verbose_name="Criação em Lote"
    )
    doc_uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name="UUID")
    task_create_document = models.CharField(max_length=256, default="", verbose_name="Task de criação de documento")
    task_submit_to_esignature = models.CharField(max_length=256, default="", verbose_name="Task de assinatura")
    submit_to_esignature = models.BooleanField(default=False, verbose_name="Enviar para assinatura eletrônica?")

    mongo_uuid = models.CharField(
        max_length=256, default="", verbose_name="UUID do Mongo"
    )

    def __str__(self):
        return self.name + " - " + self.school.name


class DocumentESignatureLog(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    esignature_log = models.TextField(
        blank=True, verbose_name="Andamentos da Assinatura Eletrônica"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Documento",
        related_name="logs",
    )

    def __str__(self):
        return self.esignature_log + " | " + str(self.created_date)


class DocumentTaskView(TenantAwareModel):
    name = models.CharField(max_length=512, verbose_name="Nome")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    signing_provider = models.CharField(
        max_length=256, default="", verbose_name="Provedor"
    )
    envelope_id = models.CharField(
        max_length=256, default="", verbose_name="Id do Envelope"
    )
    document_status = models.CharField(max_length=256, default="", verbose_name="Status do Documento")
    ged_id = models.CharField(
        max_length=128, default="", verbose_name="ID do Documento no GED"
    )
    ged_link = models.CharField(max_length=256, default="", verbose_name="Link")
    ged_uuid = models.CharField(
        max_length=256,
        default="",
        help_text="UUID do documento. UUID = Universally Unique ID.",
        verbose_name="UUID",
    )
    description = models.TextField(default="", verbose_name="Descrição")
    interview = models.ForeignKey(
        Interview, null=True, on_delete=models.CASCADE, verbose_name="Modelo"
    )
    school = models.ForeignKey(
        School, null=True, on_delete=models.CASCADE, verbose_name="Escola"
    )
    related_documents = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="documents",
    )
    document_data = JSONField(null=True, verbose_name="Dados do Documento")

    bulk_generation = models.ForeignKey(
        BulkDocumentGeneration, null=True, on_delete=models.CASCADE, verbose_name="Criação em Lote"
    )
    doc_uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name="UUID")
    task_create_document = models.CharField(max_length=256, default="", verbose_name="Task de criação de documento")
    task_submit_to_esignature = models.CharField(max_length=256, default="", verbose_name="Task de assinatura")
    submit_to_esignature = models.BooleanField(default=False, verbose_name="Enviar para assinatura eletrônica?")

    mongo_uuid = models.CharField(
        max_length=256, default="", verbose_name="UUID do Mongo"
    )

    task_name = models.CharField(
        null=True, max_length=255,
        verbose_name='Nome da Task',
        )

    task_status = models.CharField(
        max_length=50,
        verbose_name="Status da Task",
    )

    task_created_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name= 'Criação da Task',

    )
    task_done_date = models.DateTimeField(
        auto_now=True, db_index=True,
        verbose_name='Término da Task'
    )
    traceback = models.TextField(
        blank=True, null=True,
        verbose_name="Traceback"
    )

    def __str__(self):
        return self.name + " - " + self.task_status

    class Meta:
        managed = False
        db_table = 'document_task'


class EnvelopeLog(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    envelope_id = models.CharField(max_length=256, verbose_name="ID")
    status = models.CharField(max_length=256, verbose_name="Status")
    envelope_created_date = models.DateTimeField(verbose_name="Criação do envelope")
    sent_date = models.DateTimeField(null=True, verbose_name="Envio")
    # salva o TimeGenerated - Specifies the time of the status change.
    status_update_date = models.DateTimeField(verbose_name="Alteração do status")

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Documento",
        related_name="envelops_logs")

    class Meta:
        ordering = ["-envelope_created_date"]
        verbose_name = "Andamento da Assinatura Eletrônica"
        verbose_name_plural = "Andamentos da Assinatura Eletrônica"
        indexes = [
            models.Index(fields=['envelope_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.created_date)


class SignerLog(models.Model):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    name = models.CharField(max_length=256, verbose_name="Nome")
    email = models.EmailField(max_length=256, verbose_name="E-mail")
    status = models.CharField(max_length=256, verbose_name="Status")
    sent_date = models.DateTimeField(verbose_name="Envio")

    envelope_log = models.ForeignKey(
        EnvelopeLog,
        on_delete=models.CASCADE,
        verbose_name="Andamento da Assinatura Eletrônica",
        related_name="signers_logs")

    class Meta:
        ordering = ["-sent_date"]
        verbose_name = "Signatário"
        verbose_name_plural = "Signatários"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.imported_date)
