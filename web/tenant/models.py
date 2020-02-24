from django.db import models


# For genenral informations about the structure we used here, see:
# https://books.agiliq.com/projects/django-multi-tenant/en/latest/

class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain_prefix = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )

    def __str__(self):
        return self.name


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=1)

    class Meta:
        abstract = True


class TenantGedData(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nome")
    url = models.CharField(max_length=512, null=True, blank=True, verbose_name="URL")
    token = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Token da API"
    )
    database = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Banco de Dados",
    )
    database_user = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Usuário do Banco de Dados",
    )
    database_user_password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Senha do Usuário do Banco de Dados",
    )
    database_host = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Host do Banco de Dados",
    )
    database_port = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Porta do Banco de Dados",
    )
    database_database_engine = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Sistema de Banco de Dados",
        default="django.db.backends.postgresql",
    )

    storage_provider = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Fornecedor de Armazenamento",
    )

    storage_access_key = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Access Key Token"
    )

    storage_secret_key = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Secret Key"
    )

    storage_bucket_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Nome do Bucket"
    )

    storage_default_acl = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="ACL padrão",
        default="private",
    )

    storage_endpoint_url = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="URL do Endpoint"
    )

    storage_region_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Região"
    )

    def __str__(self):
        return self.name


class TenantESignatureData(models.Model):

    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, primary_key=True)

    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nome")

    provider = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="Docusign",
        verbose_name="Fornecedor",
    )

    client_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Client ID", help_text='AKA Integration Key'
    )

    impersonated_user_guid = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Impersonated User", help_text='AKA API Username'
    )

    test_mode = models.BooleanField(
        null=True, blank=True, default=True, verbose_name="Test Mode"
    )

    private_key = models.TextField(null=True, blank=True, verbose_name="Private Key")

    def __str__(self):
        return self.name
