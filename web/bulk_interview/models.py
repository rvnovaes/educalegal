from django.db import models
from django.contrib.postgres.fields import JSONField


from tenant.models import TenantAwareModel
from interview.models import Interview


# Create your models here.
class BulkGeneration(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    interview = models.ForeignKey(
        Interview, null=True, on_delete=models.CASCADE, verbose_name="Modelo"
    )
    interview_fields = JSONField(
        null=True, verbose_name="Campos e Tipos de Campo do Documento"
    )
    source_file = models.FileField()
