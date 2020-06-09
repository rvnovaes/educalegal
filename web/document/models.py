from django.db import models
from django.contrib.postgres.fields import JSONField

from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School
from bulk_interview.models import BulkGeneration


class Document(TenantAwareModel):
    name = models.CharField(max_length=512, verbose_name="Nome")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    signing_provider = models.CharField(
        max_length=256, blank=True, verbose_name="Provedor"
    )
    envelope_id = models.CharField(
        max_length=256, blank=True, verbose_name="Id do Envelope"
    )
    status = models.CharField(max_length=256, blank=True, verbose_name="Status")
    ged_id = models.CharField(
        max_length=128, null=True, blank=True, verbose_name="ID do Documento no GED"
    )
    ged_link = models.CharField(max_length=256, null=True, blank=True, verbose_name="Link")
    ged_uuid = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        help_text="UUID do documento. UUID = Universally Unique ID.",
        verbose_name="UUID",
    )
    description = models.TextField(blank=True, verbose_name="Descrição")
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

    # bulk_generation = models.ForeignKey(
    #     BulkGeneration, null=True, on_delete=models.CASCADE, verbose_name="Criação em Lote"
    # )
    #
    # mongo_id = models.CharField(max_length=256, null=True, blank=True, verbose_name="Id do documento no Mongo")
    #
    # task_create_document = models.CharField(max_length=256, null=True, blank=True, verbose_name="Task de Criação de Documento")
    #
    # task_submit_to_esignature = models.CharField(max_length=256, null=True, blank=True, verbose_name="Task de Assinatura")

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
