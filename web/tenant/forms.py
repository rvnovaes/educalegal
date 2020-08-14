from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator

from allauth.account.forms import SignupForm

from tenant.models import (
    Tenant,
    TenantGedData,
    ESignatureApp
)
from interview.models import Interview
from billing.models import Plan

class EducaLegalSignupForm(SignupForm):
    full_name = forms.CharField(label="Nome Completo", required=True)
    tenant_name = forms.CharField(label="Nome da Escola", required=True)
    phone = forms.CharField(
        label="Telefone/Whatsapp",
        required=True,  # Note: validators are not run against empty fields
        help_text="Formatos válidos para o telefone: (00) 0000-0000 ou (00) 00000-0000.",
        validators=[RegexValidator(r"\([0-9]{2}\) [0-9]{4,5}-[0-9]{4}",
                                   "Formatos válidos para o telefone: (00) 0000-0000 ou (00) 00000-0000.")]
    )

    eua = forms.BooleanField(
        label="Concordo com a política de privacidade e os termos de uso", required=True
    )

    field_order = ["full_name", "tenant_name", "phone", "email", "password1", "password2", "eua"]

    def clean(self):
        super().clean()
        try:
            Tenant.objects.get(name=self.cleaned_data.get("tenant_name"))
            self.add_error(
                "tenant_name",
                "Já existe uma escola com esse nome. Favor escolher um nome diferente ou pedir à sua escola que o cadastre como usuário.",
            )
        except ObjectDoesNotExist:
            return self.cleaned_data

    def save(self, request):
        essential_plan = Plan.objects.get(pk=1)

        tenant = Tenant.objects.create(
            name=self.cleaned_data.get("tenant_name"),
            subdomain_prefix=None,
            eua_agreement=self.cleaned_data.get("eua"),
            plan=essential_plan,
            auto_enrolled=True,
            esignature_app=None,
            phone=self.cleaned_data.get("phone"),
        )
        tenant.save()
        # Selects every freemium interview and adds to newly created tenant
        freemium_interviews = Interview.objects.filter(is_freemium=True)
        # https://docs.djangoproject.com/en/3.0/ref/models/relations/#django.db.models.fields.related.RelatedManager.add
        # add não aceita uma lista, mas um número arbitrário de objetos. Para expandir uma lista em vários objetos,
        # usamos *freemium_interviews antes da lista
        tenant.interview_set.add(*freemium_interviews)
        # Creates the user
        user = super().save(request)
        # Sets the newly created tenant to be user's tenant
        user.tenant = tenant
        # Splits the full name field into first and "rest of the name" for the user
        full_name = self.cleaned_data.get("full_name")
        user.first_name = full_name.split()[0]
        last_name = ""
        for name in full_name.split()[1:]:
            last_name += " " + name
        user.last_name = last_name
        user.save()

        return user
