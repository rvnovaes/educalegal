from enum import Enum

from django.db import models

from school.models import School
from tenant.models import TenantAwareModel


class LegalType(Enum):
    FISICA = 'F'
    JURIDICA = 'J'

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
        label = {'F': 'Física', 'J': 'Jurídica'}
        return label.get(value)


class Person(TenantAwareModel):
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Criação", blank=True)
    altered_date = models.DateTimeField(auto_now=True, verbose_name="Alteração")
    legal_name = models.CharField(
        max_length=255, blank=False, verbose_name='Razão social/Nome completo')
    name = models.CharField(max_length=255, blank=True, verbose_name='Nome Fantasia/Apelido')
    legal_type = models.CharField(
        null=False,
        blank=False,
        verbose_name='Tipo',
        max_length=1,
        choices=((x.value, x.format(x.value)) for x in LegalType),
        default=LegalType.FISICA)
    # como tem unique=True e o campo nao eh obrigatorio, deve ter null=True
    cpf_cnpj = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name='CPF/CNPJ')
    school = models.ForeignKey(School, on_delete=models.PROTECT, verbose_name="Escola")

    class Meta:
        ordering = ['legal_name', 'name']
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

    def __str__(self):
        return self.legal_name


class ContactMechanism(TenantAwareModel):
    # como tem unique_together e o campo nao eh obrigatorio, deve ter null=True
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="Email")
    # como tem unique_together e o campo nao eh obrigatorio, deve ter null=True
    phone = models.CharField(max_length=255, blank=True, null=True, verbose_name="Telefone")
    esignature_key = models.CharField(max_length=255, blank=True, verbose_name="Chave no app de assinatura eletrônica")
    notes = models.CharField(max_length=400, blank=True, verbose_name="Observações")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Meio de contato'
        verbose_name_plural = 'Meios de contato'
        unique_together = (('email', 'person'), ('phone', 'person'),)

    def __str__(self):
        return self.email if self.email else self.phone
