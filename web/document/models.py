from django.db import models
from django.contrib.postgres.fields import JSONField

from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School


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


class EnvelopeLog(models.Model):
    imported_date = models.DateTimeField(auto_now_add=True, verbose_name="Importação")
    envelope_id = models.CharField(max_length=256, verbose_name="ID")
    status = models.CharField(max_length=256, verbose_name="Status")
    created_date = models.DateTimeField(verbose_name="Criação")
    sent_date = models.DateTimeField(null=True, verbose_name="Envio")
    # salva o TimeGenerated - Specifies the time of the status change.
    status_update_date = models.DateTimeField(verbose_name="Alteração do status")

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        verbose_name="Documento",
        related_name="envelops_logs")

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "Andamento da Assinatura Eletrônica"
        verbose_name_plural = "Andamentos da Assinatura Eletrônica"
        indexes = [
            models.Index(fields=['envelope_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.created_date)


class SignerLog(models.Model):
    imported_date = models.DateTimeField(auto_now_add=True, verbose_name="Importação")
    name = models.CharField(max_length=256, verbose_name="Nome")
    email = models.EmailField(max_length=256, verbose_name="E-mail")
    status = models.CharField(max_length=256, verbose_name="Status")

    envelope_log = models.ForeignKey(
        EnvelopeLog,
        on_delete=models.CASCADE,
        verbose_name="Andamento da Assinatura Eletrônica",
        related_name="signers_logs")

    class Meta:
        ordering = ["-imported_date"]
        verbose_name = "Signatário"
        verbose_name_plural = "Signatários"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.status + " | " + str(self.imported_date)
