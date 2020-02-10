from django.db import models
from tenant.models import Tenant


class Interview(models.Model):
    name = models.CharField(max_length=512, null=True)
    version = models.CharField(max_length=512, null=True)
    date_available = models.DateField(null=True)
    description = models.TextField(null=True)
    base_url = models.URLField(max_length=512)
    tenants = models.ManyToManyField(Tenant, related_name='tenants')

    def __str__(self):
        return self.name
