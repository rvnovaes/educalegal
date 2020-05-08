import datetime
from django.db import models
from tenant.models import Tenant


class InterviewDocumentType(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return "{} - {}".format(self.pk, self.name)


class ServerConfig(models.Model):
    """ Document assembling platform server settings """
    name = models.CharField(max_length=255, verbose_name="Nome", unique=True)
    base_url = models.CharField(max_length=255, verbose_name="URL Base")
    user_id = models.IntegerField()
    username = models.CharField(max_length=255)
    user_key = models.CharField(max_length=255)
    user_password = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255, verbose_name="Nome do projeto", default='Default')

    class Meta:
        ordering = ["name"]
        verbose_name = "Configuração do Servidor"
        verbose_name_plural = "Configurações do servidor"

    def __str__(self):
        return self.name


class Interview(models.Model):
    name = models.CharField(max_length=512, verbose_name="Nome", unique=True)
    version = models.CharField(max_length=30, verbose_name="Versão")
    date_available = models.DateField(
        verbose_name="Data de Disponibilização", default=datetime.date.today
    )
    description = models.TextField(blank=True, verbose_name="Descrição")
    language = models.CharField(max_length=64, default="por", verbose_name="Idioma")
    custom_file_name = models.CharField(
        max_length=64, verbose_name="Nome do arquivo a ser gerado"
    )
    base_url = models.CharField(max_length=512, verbose_name="URL Base")
    is_generic = models.BooleanField(default=True, verbose_name="É Genérica?")
    is_freemium = models.BooleanField(default=False, verbose_name="É Freemium?")
    tenants = models.ManyToManyField(Tenant)
    document_type = models.ForeignKey(InterviewDocumentType, on_delete=models.PROTECT)
    use_bulk_interview = models.BooleanField(default=False, verbose_name="Usa geração em lote?")
    yaml_name = models.CharField(max_length=255, verbose_name="Nome do YAML", default='yml')
    server_config = models.ForeignKey(ServerConfig, on_delete=models.PROTECT, related_name='interviews', default=1)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # salva primeiro o server config da entrevista para poder montar a url depois
        Interview.objects.filter(pk=self.pk).update(server_config=self.server_config)

        server_config = ServerConfig.objects.get(interviews=self.pk)
        # monta url da entrevista de acordo com parametros da configuracao do servidor escolhido
        if server_config:
            if server_config.base_url[-1] == '/':
                url = server_config.base_url
            else:
                url = server_config.base_url + '/'
            user_id = server_config.user_id
            project_name = server_config.project_name
            yaml_name = self.yaml_name
            base_url = '{url}interview?i=docassemble.playground{user_id}{project_name}%3A{yaml_name}'.format(
                url=url, user_id=user_id, project_name=project_name, yaml_name=yaml_name
            )

        self.base_url = base_url
        super(Interview, self).save(*args, **kwargs)

    @property
    def list_tenants(self):
        list_tenants = [x.__str__() for x in self.tenants.all().order_by("name")]
        return list_tenants

    list_tenants.fget.short_description = "Instâncias"
