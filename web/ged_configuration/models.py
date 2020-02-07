from django.db import models
from tenant.models import TenantAwareModel


class GEDConfiguration(TenantAwareModel):

    ged_url = models.CharField(max_length=255, null=True, blank=True,
                               verbose_name='URL do GED')
    token = models.CharField(max_length=255, null=True, blank=True,
                               verbose_name='Token da API')

    def __str__(self):
        return self.ged_url



