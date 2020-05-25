import datetime
from django.db import models
from tenant.models import Tenant


class InterviewDocumentType(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return "{} - {}".format(self.pk, self.name)


class InterviewServerConfig(models.Model):
    """ Document assembling platform server settings """

    name = models.CharField(max_length=255, verbose_name="Nome", unique=True)
    base_url = models.CharField(max_length=255, verbose_name="URL Base")
    user_id = models.IntegerField()
    username = models.CharField(max_length=255)
    user_key = models.CharField(max_length=255)
    user_password = models.CharField(max_length=255)
    project_name = models.CharField(
        max_length=255, verbose_name="Nome do projeto", default="Default"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Configuração do Servidor de Entrevistas"
        verbose_name_plural = "Configurações do Servidor de Entrevistas"

    def __str__(self):
        return self.name


class Interview(models.Model):
    name = models.CharField(max_length=512, verbose_name="Nome", unique=True)
    version = models.CharField(max_length=30, verbose_name="Versão")
    date_available = models.DateField(
        verbose_name="Disponibilização", default=datetime.date.today
    )
    description = models.TextField(blank=True, verbose_name="Descrição")
    language = models.CharField(max_length=64, default="por", verbose_name="Idioma")
    custom_file_name = models.CharField(
        max_length=255, verbose_name="Nome do arquivo a ser gerado"
    )
    base_url = models.URLField(
        null=True,
        blank=True,
        default="",
        verbose_name="URL Customizada",
        help_text="O valor desse campo sobrescreve qualquer valor de configuração de Servidor de Entrevistas. Deve ser usado para inserir URLs arbitrárias de entrevistas.",
    )
    is_generic = models.BooleanField(
        default=True,
        verbose_name="Inserir dados de acesso?",
        help_text="Se marcado, insere na URL da entrevista os parâmetros de acesso (tenand id, user token, e interview id).",
    )
    is_freemium = models.BooleanField(
        default=False,
        verbose_name="É Freemium?",
        help_text="Se marcado, a entrevista é disponibilizada para o cliente (tenant) que se auto inscreve no site.",
    )
    tenants = models.ManyToManyField(Tenant)
    document_type = models.ForeignKey(InterviewDocumentType, on_delete=models.PROTECT)
    use_bulk_interview = models.BooleanField(
        default=False, verbose_name="Usa geração em lote?"
    )
    yaml_name = models.CharField(
        max_length=255, verbose_name="Nome do YAML", default="yml"
    )
    interview_server_config = models.ForeignKey(
        InterviewServerConfig,
        on_delete=models.PROTECT,
        related_name="interviews",
        default=1,
        verbose_name="Servidor de Entrevistas",
        help_text="Configuração do Servidor de Entrevistas usado para montar a URL da entrevista. Esse valor é sobrescrito se o valor URL customizada for preenchido.",
    )

    def __str__(self):
        return self.name

    @property
    def list_tenants(self):
        list_tenants = [x.__str__() for x in self.tenants.all().order_by("name")]
        return list_tenants

    list_tenants.fget.short_description = "Instâncias"
