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
