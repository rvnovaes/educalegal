from enum import Enum
from django.conf import settings
from django.db import models
from django.urls import reverse


from audit.models import Audit

# Podem ser melhoradas)
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
                          (EMAIL, 'E-MAIL'), (SKYPE, 'SKYPE'), (WHATSAPP, 'WHATSAPP'),
                          (FACEBOOK, 'FACEBOOK'), (SITE, 'SITE'), (LINKEDIN, 'LINKEDIN'),
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


class AddressType(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        verbose_name = 'Tipo de Endereço'
        verbose_name_plural = 'Tipos de Endereço'

    def __str__(self):
        return self.name


class Country(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['name']

    def __str__(self):
        return self.name


class State(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)
    initials = models.CharField(max_length=10, null=False, unique=True)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['name']

    def __str__(self):
        return self.name


class City(Audit):
    name = models.CharField(max_length=255, null=False)
    state = models.ForeignKey(
        State, on_delete=models.PROTECT, blank=False, null=False)

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        unique_together = ('name', 'state')

    def __str__(self):
        return '{} - {}'.format(self.name, self.state.initials)


class AbstractPerson(Audit):
    legal_name = models.CharField(
        max_length=255, blank=False, verbose_name='Razão social/Nome completo')
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Nome Fantasia/Apelido')
    legal_type = models.CharField(
        null=False,
        verbose_name='Tipo',
        max_length=1,
        choices=((x.value, x.format(x.value)) for x in LegalType),
        default=LegalType.JURIDICA)
    cpf_cnpj = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name='CPF/CNPJ')

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

    class Meta:
        abstract = True

    def __str__(self):
        return self.legal_name or ''


class Company(AbstractPerson):
    logo = models.ImageField(verbose_name='Logo', null=True, blank=True)
    units = models.ManyToManyField('self', blank=True, symmetrical=False)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def get_absolute_url(self):
        return reverse('person:company-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.legal_name


class Person(AbstractPerson):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Empresa'
    )

    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Usuário do sistema')

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'


class Address(Audit):
    street = models.CharField(max_length=255, verbose_name='Logradouro')
    street_number = models.CharField(max_length=255, verbose_name='Número')
    unit = models.CharField(
        max_length=255, blank=True, verbose_name='Complemento')
    city_region = models.CharField(max_length=255, verbose_name='Bairro')
    zip_code = models.CharField(max_length=255, verbose_name='CEP')
    address_type = models.ForeignKey(
        AddressType,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='Tipo')
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='Cidade')
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='Estado')
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name='País')
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, blank=True, null=True)
    # abstract_person = models.ForeignKey(
    #     AbstractPerson, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        tpl = '{street}, {number}{complement} - {city_region} - {city} - {state} - CEP {zip_code}'
        return tpl.format(
            number=self.street_number,
            street=self.street,
            city_region=self.city_region,
            city=self.city.name,
            state=self.state.name,
            zip_code=self.zip_code,
            complement='/' + self.unit if self.unit else '')


class ContactMechanismType(Audit):
    name = models.CharField(max_length=255, null=False, unique=True)
    type_contact_mechanism_type = models.IntegerField(
        choices=CONTACT_MECHANISM_TYPE,
        verbose_name='Tipo',
        default=PHONE,
        null=False)

    def is_email(self):
        return self.type_contact_mechanism_type == EMAIL

    def __str__(self):
        return self.name


class ContactMechanism(Audit):
    description = models.CharField(
        max_length=255, null=False, verbose_name="Descrição")
    notes = models.CharField(
        max_length=400, blank=True, verbose_name="Observações")
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, blank=True, null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, blank=True, null=True)

    contact_mechanism_type = models.ForeignKey(
        ContactMechanismType,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        verbose_name="Tipo")

    class Meta:
        verbose_name = 'Mecanismo de contato'
        verbose_name_plural = 'Mecanismos de contato'
        unique_together = (('description', 'person'), ('description', 'company'))

    def __str__(self):
        return self.description
