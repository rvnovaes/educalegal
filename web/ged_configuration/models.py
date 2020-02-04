from django.db import models
from person.models import Company


class Configuration(models.Model):

    ged_url = models.CharField(max_length=255, null=True, blank=True,
                               verbose_name='URL do GED')

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Empresa'
    )