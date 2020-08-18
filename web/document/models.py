import uuid

from enum import Enum

from django.db import models
# from django.contrib.postgres.fields import JSONField
from django.db.models import JSONField

from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School


class DocumentStatus(Enum):
    RASCUNHO = "rascunho"
    CRIADO = "criado"
    INSERIDO_GED = "inserido no GED"
    ENVIADO_EMAIL = "enviado por e-mail"
    ENVIADO_ASS_ELET = "enviado para assinatura"
    ASSINADO = "assinado"
    RECUSADO_INVALIDO = "assinatura recusada/inválida"
    NAO_ENCONTRADO = "não encontrado"

    def __str__(self):
        return str(self.value.lower())

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


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


class Envelope(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    identifier = models.CharField(max_length=256, verbose_name="ID")
    status = models.CharField(max_length=256, verbose_name="Status")
    envelope_created_date = models.DateTimeField(verbose_name="Criação do envelope")
    sent_date = models.DateTimeField(null=True, verbose_name="Envio")
    # salva o TimeGenerated - Specifies the time of the status change.
    status_update_date = models.DateTimeField(null=True, verbose_name="Alteração do status")
    signing_provider = models.CharField(
        max_length=256, blank=True, default="", verbose_name="Provedor"
    )
    envelope_log_id = models.IntegerField(null=True, blank=True, verbose_name="envelope_log_id")

    class Meta:
        ordering = ["-envelope_created_date"]
        verbose_name = "Envelope"
        verbose_name_plural = "Envelopes"
        indexes = [
            models.Index(fields=['identifier']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.created_date)


class Document(TenantAwareModel):
    name = models.CharField(max_length=512, verbose_name="Nome")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    envelope_number = models.CharField(
        max_length=256, blank=True, default="", verbose_name="N° do Envelope"
    )
    status = models.CharField(max_length=256, default="", verbose_name="Status")
    ged_id = models.CharField(
        max_length=128, blank=True, default="", verbose_name="ID do Documento no GED"
    )
    ged_link = models.CharField(max_length=256, blank=True, default="", verbose_name="Link")
    ged_uuid = models.CharField(
        max_length=256,
        blank=True,
        default="",
        help_text="UUID do documento. UUID = Universally Unique ID.",
        verbose_name="UUID",
    )
    description = models.TextField(default="", blank=True, verbose_name="Descrição")
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
    task_create_document = models.CharField(max_length=256, blank=True, default="", verbose_name="Task de criação de documento")
    task_submit_to_esignature = models.CharField(max_length=256, blank=True, default="", verbose_name="Task de assinatura")
    task_send_email = models.CharField(max_length=256, blank=True, default="", verbose_name="Task de envio de e-mail")
    submit_to_esignature = models.BooleanField(default=False, verbose_name="A Elet")
    send_email = models.BooleanField(default=False, verbose_name="E-mail?")
    mongo_uuid = models.CharField(
        max_length=256, blank=True, default="", verbose_name="UUID do Mongo"
    )

    envelope = models.ForeignKey(
        Envelope,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Envelope",
        related_name="documents")

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"
        indexes = [
            models.Index(fields=['envelope_number']),
        ]

    def __str__(self):
        if self.school is not None:
            return self.name + ' - ' + self.school.name
        else:
            return self.name


class Signer(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    name = models.CharField(max_length=256, verbose_name="Nome")
    email = models.EmailField(max_length=256, verbose_name="E-mail")
    type = models.CharField(max_length=256, verbose_name="Tipo")
    status = models.CharField(max_length=256, verbose_name="Status")
    sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Envio")
    pdf_filenames = models.TextField(blank=True, verbose_name="PDFs")
    envelope_log_id = models.IntegerField(null=True, blank=True, verbose_name="envelope_log_id")
    signer_log_id = models.IntegerField(null=True, blank=True, verbose_name="signer_log_id")

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Documento",
        related_name="signers")

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "Signatário"
        verbose_name_plural = "Signatários"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.created_date)


# DEPRECATED - Um dia vamos apagar você - Huahauahauha TODO
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
    task_send_email = models.CharField(max_length=256, default="", verbose_name="Task de envio de e-mail")
    submit_to_esignature = models.BooleanField(default=False, verbose_name="A Elet")
    send_email = models.BooleanField(default=False, verbose_name="E-mail")

    mongo_uuid = models.CharField(
        max_length=256, default="", verbose_name="UUID do Mongo"
    )

    task_name = models.CharField(
        null=True, max_length=255,
        verbose_name='Nome da Tarefa',
        )

    task_status = models.CharField(
        max_length=50,
        verbose_name="Status da Tarefa",
    )

    task_created_date = models.DateTimeField(
        auto_now_add=True, db_index=True,
        verbose_name= 'Criação da Tarefa',

    )
    task_done_date = models.DateTimeField(
        auto_now=True, db_index=True,
        verbose_name='Término da Tarefa'
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


class EnvelopeLog(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    envelope_id = models.CharField(max_length=256, verbose_name="ID")
    status = models.CharField(max_length=256, verbose_name="Status")
    envelope_created_date = models.DateTimeField(verbose_name="Criação do envelope")
    sent_date = models.DateTimeField(null=True, verbose_name="Envio")
    # salva o TimeGenerated - Specifies the time of the status change.
    status_update_date = models.DateTimeField(null=True, verbose_name="Alteração do status")

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Documento",
        related_name="envelope_logs")

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


class SignerLog(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    name = models.CharField(max_length=256, verbose_name="Nome")
    email = models.EmailField(max_length=256, verbose_name="E-mail")
    type = models.CharField(max_length=256, verbose_name="Tipo")
    status = models.CharField(max_length=256, verbose_name="Status")
    sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Envio")
    pdf_filenames = models.TextField(blank=True, verbose_name="PDFs")

    envelope_log = models.ForeignKey(
        EnvelopeLog,
        on_delete=models.CASCADE,
        verbose_name="Andamento da Assinatura Eletrônica",
        related_name="signer_logs")

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "Signatário"
        verbose_name_plural = "Signatários"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.created_date)
