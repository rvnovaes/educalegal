import datetime
from django.db import models
from tenant.models import Tenant


class InterviewDocumentType(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return '{} - {}'.format(self.pk, self.name)


class Interview(models.Model):
    name = models.CharField(max_length=512, verbose_name='Nome', unique=True)
    version = models.CharField(max_length=30, verbose_name='Versão')
    date_available = models.DateField(verbose_name='Data de Disponibilização', default=datetime.date.today)
    description = models.TextField(blank=True, verbose_name='Descrição')
    language = models.CharField(max_length=64, default='por', verbose_name='Idioma')
    custom_file_name = models.CharField(max_length=64, verbose_name='Nome do arquivo a ser gerado')
    base_url = models.URLField(max_length=512, verbose_name='URL Base')
    is_generic = models.BooleanField(default=True, verbose_name='É Genérica?')
    tenants = models.ManyToManyField(Tenant, related_name='tenants')
    document_type = models.ForeignKey(InterviewDocumentType, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    @property
    def list_tenants(self):
        list_tenants = [x.__str__() for x in self.tenants.all().order_by('name')]
        return list_tenants

    list_tenants.fget.short_description = 'Instâncias'
