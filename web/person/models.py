from enum import Enum

from django.conf import settings
from django.db import models
from django.utils.translation import gettext, gettext_lazy as _


INVALIDO = 1
PHONE = 2
EMAIL = 3
SKYPE = 4
WHATSAPP = 5
FACEBOOK = 6
SITE = 7
LINKEDIN = 8
INSTAGRAM = 9
SNAPCHAT = 10
CONTACT_MECHANISM_TYPE = ((INVALIDO, 'INVÁLIDO'), (PHONE, 'TELEFONE'),
                          (EMAIL, 'E-MAIL'), (SKYPE, 'SKYPE'), (WHATSAPP,
                                                                'WHATSAPP'),
                          (FACEBOOK, 'FACEBOOK'), (SITE, 'SITE'), (LINKEDIN,
                                                                   'LINKEDIN'),
                          (INSTAGRAM, 'INSTAGRAM'), (SNAPCHAT, 'SNAPCHAT'))


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


class ContactMechanismType(models.Model):
    type_contact_mechanism_type = models.IntegerField(
        choices=CONTACT_MECHANISM_TYPE,
        verbose_name='Tipo',
        default=PHONE,
        null=False)
    name = models.CharField(max_length=255, null=False, unique=True)

    def is_email(self):
        return self.type_contact_mechanism_type == EMAIL

    class Meta:
        db_table = 'contact_mechanism_type'

    def __str__(self):
        return self.name


class AbstractPerson(models.Model):
    legal_name = models.CharField(
        max_length=255, blank=False, verbose_name=_('Razão social/Nome completo'))
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Nome Fantasia/Apelido'))
    legal_type = models.CharField(
        null=False,
        verbose_name='Tipo',
        max_length=1,
        choices=((x.value, x.format(x.value)) for x in LegalType),
        default=LegalType.JURIDICA)
    tax_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_('CPF/CNPJ'))
    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name=_('Usuário do sistema'))

    @property
    def cpf(self):
        return self.cpf_cnpj

    @cpf.setter
    def cpf(self, value):
        self.cpf = value

    @property
    def cnpj(self):
        return self.cpf_cnpj

    @cnpj.setter
    def cnpj(self, value):
        self.cnpj = value

    def contact_mechanism_by_type(self, mechanism_type, formated=True):
        mechanism_type = ContactMechanismType.objects.filter(
            name__iexact=mechanism_type).first()
        contacts = self.contactmechanism_set.filter(
            contact_mechanism_type=mechanism_type)
        items = [contact.description for contact in contacts]
        if formated:
            return ' | '.join(items) if items else ''
        return items

    @property
    def emails(self):
        emails = self.get_emails()
        return ' | '.join(emails) if emails else ''

    @property
    def phones(self):
        return self.contact_mechanism_by_type('telefone')

    def get_emails(self):
        emails = self.contact_mechanism_by_type('e-mail', formated=False)
        emails = set(emails)
        if (self.auth_user and self.auth_user.email
                and self.auth_user.email.strip()):
            emails.add(self.auth_user.email.strip())
        return list(emails)

    def get_phones(self):
        return self.contact_mechanism_by_type('telefone', formated=False)

    def get_address(self):
        return self.address_set.exclude(id=1)

    @property
    def is_admin(self):
        return True if self.auth_user.groups.filter(name__startswith=self.ADMINISTRATOR_GROUP).first() \
            else False

    @property
    def is_correspondent(self):
        return True if self.auth_user.groups.filter(name__startswith=self.CORRESPONDENT_GROUP).first() \
            else False

    @property
    def is_requester(self):
        return True if self.auth_user.groups.filter(name__startswith=self.REQUESTER_GROUP).first() \
            else False

    @property
    def is_service(self):
        return True if self.auth_user.groups.filter(name__startswith=self.SERVICE_GROUP).first() \
            else False

    @property
    def is_supervisor(self):
        return True if self.auth_user.groups.filter(name__startswith=self.SUPERVISOR_GROUP).first() \
            else False

    @property
    def is_company_representative(self):
        return True if self.auth_user.groups.filter(name__startswith=self.COMPANY_REPRESENTATIVE).first() \
            else False

    class Meta:
        abstract = True

    def __str__(self):
        return self.legal_name or ''


class Company(models.Model):
    logo = models.ImageField(verbose_name='Logo', null=True, blank=True)
    name = models.CharField(verbose_name='Empresa', max_length=255)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.name

class Person(AbstractPerson):

    cpf_cnpj = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=False,
        verbose_name='CPF/CNPJ')
    create_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_create_user',
        verbose_name='Criado por')
    alter_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='%(class)s_alter_user',
        verbose_name='Alterado por')

    company = models.ForeignKey(
        Company,
        verbose_name='Compartilhar com empresa',
        null=True,
        blank=True)

    refunds_correspondent_service = models.BooleanField(
        null=False, default=False, verbose_name='Cliente reembolsa valor gasto com serviço de correspondência')

    class Meta:
        db_table = 'person'
        ordering = ['legal_name', 'name']
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'

    def simple_serialize(self):
        """Simple JSON representation of instance"""
        return {
            "id": self.id,
            "legal_name": self.legal_name,
            "name": self.name
        }


class ContactMechanism(models.Model):
    contact_mechanism_type = models.ForeignKey(
        ContactMechanismType,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tipo")
    description = models.CharField(
        max_length=255, null=False, verbose_name="Descrição")
    notes = models.CharField(
        max_length=400, blank=True, verbose_name="Observações")
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'contact_mechanism'
        verbose_name = 'Mecanismo de contato'
        verbose_name_plural = 'Mecanismos de contato'
        unique_together = (('description', 'person'))

    def __str__(self):
        return self.description



