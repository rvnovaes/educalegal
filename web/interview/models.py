from django.db import models
from tenant.models import TenantAwareModel


class Interview(TenantAwareModel):
    name = models.CharField(max_length=512, null=True)
    version = models.CharField(max_length=512, null=True)
    date_available = models.DateField(null=True)
    description = models.TextField(null=True)
    url = models.URLField(max_length=512)

    def __str__(self):
        return self.name
