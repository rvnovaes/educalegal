from django.db import models
from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School


class Document(TenantAwareModel):
    name = models.CharField(max_length=512, null=True, verbose_name="Nome")
    main_document = models.BooleanField(blank=True, null=True, verbose_name='Documento Principal')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    status = models.CharField(
        max_length=256, null=True, blank=True, verbose_name="Status"
    )
    envelope_id = models.CharField(
        max_length=256, null=True, blank=True, verbose_name="Id do Envelope"
    )
    signing_provider = models.CharField(
        max_length=256, null=True, blank=True, verbose_name="Provedor"
    )
    ged_id = models.CharField(max_length=128, null=True, blank=True, verbose_name='ID do Documento no GED')
    ged_link = models.CharField(max_length=256, null=True, blank=True, verbose_name="Link")
    ged_uuid = models.CharField(
        max_length=256,
        null=True,
        help_text="UUID do documento. UUID = Universally Unique ID.",
        verbose_name="UUID",
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descrição")
    interview = models.ForeignKey(
        Interview, null=True, on_delete=models.CASCADE, verbose_name="Modelo"
    )
    school = models.ForeignKey(
        School, null=True, on_delete=models.CASCADE, verbose_name="Escola"
    )
    related_documents = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="documents"
    )

    def __str__(self):
        return self.name + " - " + self.school.name


class DocumentESignatureLog(TenantAwareModel):
    esignature_log = models.TextField(null=True, blank=True, verbose_name="Andamentos da Assinatura Eletrônica")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    document = models.ForeignKey(
        Document, null=True, on_delete=models.CASCADE, verbose_name="Documento", related_name="logs"
    )

    def __str__(self):
        return self.esignature_log + ' | ' + str(self.created_date)
