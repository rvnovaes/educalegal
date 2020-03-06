from enum import Enum
from django.db import models
from django.urls import reverse

from tenant.models import TenantAwareModel


class LegalType(Enum):
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


class Country(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["name"]

    def __str__(self):
        return self.name


class State(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    initials = models.CharField(max_length=10, null=False, unique=True)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, blank=False, null=False
    )

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255, null=False)
    state = models.ForeignKey(State, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"
        unique_together = ("name", "state")

    def __str__(self):
        return self.name


class School(TenantAwareModel):
    name = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Nome Fantasia"
    )
    legal_name = models.CharField(
        max_length=255, blank=False, verbose_name="Razão social"
    )
    legal_type = models.CharField(
        null=False,
        verbose_name="Tipo",
        max_length=1,
        choices=((x.value, x.format(x.value)) for x in LegalType),
        default=LegalType.JURIDICA,
    )
    cnpj = models.CharField(
        max_length=255, blank=True, null=True, unique=True, verbose_name="CNPJ"
    )
    logo = models.ImageField(verbose_name="Logo", null=True, blank=True)
    street = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Logradouro"
    )
    street_number = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Número"
    )
    unit = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Complemento"
    )
    city_region = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Bairro"
    )
    zip_code = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="CEP"
    )
    phone = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Telefone"
    )
    site = models.URLField(null=True, blank=True, verbose_name="Site")
    email = models.EmailField(null=True, blank=True, verbose_name="E-mail")
    letterhead = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Timbrado"
    )
    city = models.ForeignKey(
        City, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Cidade"
    )
    state = models.ForeignKey(
        State, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Estado",
    )
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, blank=True, null=True, verbose_name="País"
    )

    def __str__(self):
        return self.name + ' - ' + self.legal_name

    @property
    def address(self):
        tpl = "{street}, {street_number}{unit} - {city_region} - {city} - {state} - CEP {zip_code}"
        return tpl.format(
            street_number=self.street_number if self.street_number else "",
            street=self.street if self.street else "",
            city_region=self.city_region if self.city_region else "",
            city=self.city.name if self.city else "",
            state=self.state.initials if self.state else "",
            zip_code=self.zip_code if self.zip_code else "",
            unit="/" + self.unit if self.unit else "",
        )

    def get_absolute_url(self):
        return reverse("school:school-detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = "Escola"
        verbose_name_plural = "Escolas"
