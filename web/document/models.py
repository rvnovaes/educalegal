from django.db import models
from tenant.models import TenantAwareModel
from interview.models import Interview
from school.models import School


class Document(TenantAwareModel):
    name = models.CharField(max_length=512, verbose_name="Nome")
    school = models.ForeignKey(School, on_delete=models.CASCADE, verbose_name="Escola")
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Criação"
    )
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    interview = models.ForeignKey(
        Interview, on_delete=models.CASCADE, verbose_name="Modelo"
    )
    status = models.CharField(max_length=256, verbose_name="Status")
    signing_provider = models.CharField(max_length=256, verbose_name="Provedor")
    ged_link = models.URLField(null=True, blank=True, verbose_name="Link")
    description = models.TextField(null=True, verbose_name='Descrição')
    related_documents = models.ManyToManyField('self', related_name='documents')

    def __str__(self):
        return self.name + ' - ' + self.school.name
