from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain_prefix = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )
    ged_url = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="URL do GED"
    )
    ged_token = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Token da API do GED"
    )

    def __str__(self):
        return self.name


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=1)

    class Meta:
        abstract = True
