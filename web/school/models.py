from enum import Enum
from django.db import models
from django.urls import reverse

from tenant.models import TenantAwareModel


class LegalNature(Enum):
    FISICA = "F"
    JURIDICA = "J"

    def __str__(self):
        return str(self.value)

    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]

    @staticmethod
    def format(value):
        """
        Mostra os tipos de pessoa de forma correta, com acento

        :param value: Valor selecionado sendo F ou J
        :type value: str
        :return: Retorna o valor a ser mostrado na tela para o usuario final
        :rtype: str
        """
        label = {"F": "Física", "J": "Jurídica"}
        return label.get(value)


class SignatoryKind(Enum):
    Testemunha = "Testemunha"
    Representante = "Representante"

    def __str__(self):
        return self.value

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class School(TenantAwareModel):
    legal_name = models.CharField(max_length=255, verbose_name="Razão social")
    name = models.CharField(max_length=255, blank=True, verbose_name="Nome Fantasia")
    # https://docs.djangoproject.com/en/3.0/ref/models/fields/
    # when a CharField has both unique=True and blank=True set null=True is required to
    # avoid unique constraint violations when saving multiple objects with blank values
    cnpj = models.CharField(max_length=255, verbose_name="CNPJ")
    logo = models.ImageField(verbose_name="Logo", blank=True, null=True)
    phone = models.CharField(max_length=255, verbose_name="Telefone")
    site = models.URLField(verbose_name="Site", blank=True)
    email = models.EmailField(verbose_name="E-mail")
    street = models.CharField(max_length=255, verbose_name="Logradouro")
    street_number = models.CharField(max_length=255, verbose_name="Número")
    unit = models.CharField(max_length=255, blank=True, verbose_name="Complemento")
    neighborhood = models.CharField(max_length=255, verbose_name="Bairro")
    zip = models.CharField(max_length=255, verbose_name="CEP")
    city = models.CharField(max_length=255, verbose_name="Cidade")
    state = models.CharField(max_length=255, verbose_name="Estado",)
    country = models.CharField(max_length=255, default="Brasil", verbose_name="País")
    letterhead = models.CharField(max_length=255, default="timbrado-padrao.docx", verbose_name="Timbrado")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação", blank=True)
    esignature_folder = models.CharField(max_length=255, blank=True, verbose_name="Pasta para upload dos documentos")

    class Meta:
        ordering = ["name"]
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.esignature_folder = self.esignature_folder.replace('/', '')
        self.esignature_folder = self.esignature_folder.replace('\\', '')
        super(School, self).save(*args, **kwargs)

    @property
    def address(self):
        tpl = "{street}, {street_number}{unit} - {neighborhood} - {city} - {state} - CEP {zip}"
        return tpl.format(
            street_number=self.street_number if self.street_number else "",
            street=self.street if self.street else "",
            neighborhood=self.neighborhood if self.neighborhood else "",
            city=self.city if self.city else "",
            state=self.state if self.state else "",
            zip=self.zip if self.zip else "",
            unit="/" + self.unit if self.unit else "",
        )

    def get_absolute_url(self):
        return reverse("school:school-detail", kwargs={"pk": self.pk})


class SchoolUnit(TenantAwareModel):
    name = models.CharField(max_length=255, verbose_name="Nome")
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="school_units",
        verbose_name="Escola",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Unidade Escolar"
        verbose_name_plural = "Unidades Escolares"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("school:school-unit-detail", kwargs={"pk": self.pk})


class Signatory(TenantAwareModel):
    name = models.CharField(max_length=255, verbose_name="Nome")
    email = models.EmailField(verbose_name="E-mail")
    cpf = models.CharField(max_length=255, verbose_name="CPF")
    kind = models.CharField(
        verbose_name="Tipo de Signatário da Escola",
        max_length=255,
        choices=SignatoryKind.choices(),
        default=SignatoryKind.Testemunha.value,
    )

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="signatories",
        verbose_name="Escola",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Signatário da Escola"
        verbose_name_plural = "Signatários da Escola"

    def __str__(self):
        return self.name


class Grade(TenantAwareModel):
    name = models.CharField(max_length=255, verbose_name="Nome")
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Escola",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Série"
        verbose_name_plural = "Séries"

    def __str__(self):
        return self.name
