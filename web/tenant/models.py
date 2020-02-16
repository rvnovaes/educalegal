from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain_prefix = models.CharField(
        max_length=100, blank=True, null=True, unique=True
    )
    ged_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Nome Base"
    )
    ged_url = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - URL"
    )
    ged_token = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Token da API"
    )
    ged_database = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Banco de Dados",
    )
    ged_database_user = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - Usuário do Banco de Dados",
    )
    ged_database_user_password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - Senha do Usuário do Banco de Dados",
    )
    ged_database_host = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - Host do Banco de Dados",
    )
    ged_database_port = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - Porta do Banco de Dados",
    )
    ged_database_database_engine = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - Sistema de Banco de Dados",
        default="django.db.backends.postgresql",
    )

    ged_storage_provider = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - Fornecedor de Armazenamento",
    )

    ged_storage_access_key = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Access Key Token"
    )

    ged_storage_secret_key = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Secret Key"
    )

    ged_storage_bucket_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Nome do Bucket"
    )

    ged_storage_default_acl = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="GED - ACL padrão",
        default="private",
    )

    ged_storage_endpoint_url = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - URL do Endpoint"
    )

    ged_storage_region_name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="GED - Região"
    )

    esignature_provider = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="Docusign",
        verbose_name="ESignature - Fornecedor",
    )

    esignature_client_id = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="ESignature - Client ID"
    )

    esignature_impersonate_user_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="ESignature - Impersonated User",
    )

    esignature_test_mode = models.BooleanField(
        null=True, blank=True, default=True, verbose_name="ESignature - Test Mode"
    )

    e_signature_private_key = models.TextField(
        null=True, blank=True, verbose_name="ESignature - Private Key"
    )

    def __str__(self):
        return self.name


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=1)

    class Meta:
        abstract = True
