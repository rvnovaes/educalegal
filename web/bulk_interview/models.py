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
    field_types_dict = JSONField(null=False, default={}, verbose_name="Campos do Modelo")
    required_fields_dict = JSONField(null=False, default={}, verbose_name="Obrigatoriedade dos Campos do Modelo")
    mongo_db_collection_name = models.CharField(
        max_length=1024, null=False, verbose_name="Coleção de Documentos no Mongo"
    )
