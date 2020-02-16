from django.db import models
from tenant.models import Tenant


class InterviewDocumentType(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return '{} - {}'.format(self.pk, self.name)


class Interview(models.Model):
    name = models.CharField(max_length=512, null=True, verbose_name='Nome')
    version = models.CharField(max_length=512, null=True, verbose_name='Versão')
    date_available = models.DateField(null=True, verbose_name='Data de Disponibilização')
    description = models.TextField(null=True, verbose_name='Descrição')
    base_url = models.URLField(max_length=512, verbose_name='URL Base')
    is_generic = models.BooleanField(default=True, verbose_name='É Genérica?')
    tenants = models.ManyToManyField(Tenant, related_name='tenants')
    document_type = models.ForeignKey(InterviewDocumentType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name