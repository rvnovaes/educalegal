from django.db import models
from billing.models import Plan
from enum import Enum

# For genenral informations about the structure we used here, see:
# https://books.agiliq.com/projects/django-multi-tenant/en/latest/


class ESignatureAppProvider(Enum):
    CLICKSIGN = "ClickSign"
    DOCUSIGN = "Docusign"

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class ESignatureApp(models.Model):
    name = models.CharField(
        max_length=255, default="Educa Legal Development", verbose_name="Nome da Aplicação Cliente",
    )
    provider = models.CharField(
        max_length=255,
        choices=ESignatureAppProvider.choices(),
        default=ESignatureAppProvider.CLICKSIGN.value,
        verbose_name="Fornecedor",
    )
    private_key = models.TextField(verbose_name="Private Key")
    client_id = models.CharField(
        max_length=255, verbose_name="Client ID", help_text="AKA Integration Key"
    )
    impersonated_user_guid = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Impersonated User",
        help_text="AKA API Username",
    )
    notes = models.TextField(null=True, blank=True, verbose_name="Observações")

    test_mode = models.BooleanField(default=True, verbose_name="Test Mode")

    class Meta:
        ordering = ["name"]
        verbose_name = "Aplicativo de assinatura eletrônica"
        verbose_name_plural = "Aplicativos de assinatura eletrônica"

    def __str__(self):
        return self.name


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subdomain_prefix = models.CharField(max_length=100, null=True, blank=True, unique=True)
    eua_agreement = models.BooleanField(default=True, verbose_name="Concordo com os termos de uso")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="tenants", verbose_name="Plano", default=1)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação")
    auto_enrolled = models.BooleanField(
        default=False, verbose_name="Autoinscrito"
    )
    esignature_app = models.ForeignKey(
        ESignatureApp,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        default=1,
        verbose_name='App de assinatura eletrônica')
    phone = models.CharField(max_length=50, blank=True, verbose_name="Telefone")
    esignature_folder = models.CharField(max_length=255, blank=True, verbose_name="Pasta para upload dos documentos")

    class Meta:
        ordering = ["name"]
        verbose_name = "Instância"
        verbose_name_plural = "Instâncias"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.esignature_folder = self.esignature_folder.replace('/', '')
        self.esignature_folder = self.esignature_folder.replace('\\', '')
        super(Tenant, self).save(*args, **kwargs)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, default=1)

    class Meta:
        abstract = True


class TenantGedData(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, primary_key=True)
    url = models.CharField(max_length=512, verbose_name="URL")
    token = models.CharField(max_length=255, verbose_name="Token da API")
    database = models.CharField(max_length=255, verbose_name="Banco de Dados",)
    database_user = models.CharField(
        max_length=255, verbose_name="Usuário do Banco de Dados",
    )
    database_user_password = models.CharField(
        max_length=255, verbose_name="Senha do Usuário do Banco de Dados",
    )
    database_host = models.CharField(
        max_length=255, verbose_name="Host do Banco de Dados",
    )
    database_port = models.CharField(
        max_length=255, verbose_name="Porta do Banco de Dados",
    )
    database_database_engine = models.CharField(
        max_length=255,
        verbose_name="Sistema de Banco de Dados",
        default="django.db.backends.postgresql",
    )
    storage_provider = models.CharField(
        max_length=255, verbose_name="Fornecedor de Armazenamento",
    )
    storage_access_key = models.CharField(
        max_length=255, verbose_name="Access Key Token"
    )
    storage_secret_key = models.CharField(max_length=255, verbose_name="Secret Key")
    storage_bucket_name = models.CharField(
        max_length=255, verbose_name="Nome do Bucket"
    )
    storage_default_acl = models.CharField(
        max_length=255, verbose_name="ACL padrão", default="private",
    )
    storage_endpoint_url = models.CharField(
        max_length=255, verbose_name="URL do Endpoint"
    )
    storage_region_name = models.CharField(max_length=255, verbose_name="Região")

    class Meta:
        ordering = ["tenant"]
        verbose_name = "Configuração do GED"
        verbose_name_plural = "Configurações do GED"

    def __str__(self):
        return self.url


class ESignatureAppSignerKey(TenantAwareModel):
    email = models.EmailField(max_length=255, verbose_name="E-mail")
    key = models.CharField(max_length=255, verbose_name="Chave")
    esignature_app = models.ForeignKey(
        ESignatureApp,
        on_delete=models.PROTECT,
        default=3,
        verbose_name='App de assinatura eletrônica')

    class Meta:
        ordering = ["email"]
        verbose_name = "Chave do signatário para assinatura eletrônica"
        verbose_name_plural = "Chaves do signatário para assinatura eletrônica"
        unique_together = (('email', 'tenant', 'esignature_app'),)

    def __str__(self):
        return self.email + ' - ' + self.key
