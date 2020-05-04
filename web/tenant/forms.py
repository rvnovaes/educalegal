from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group

from allauth.account.forms import SignupForm

from tenant.models import Tenant
from tenant.models import TenantGedData
from tenant.models import TenantESignatureData
from interview.models import Interview


class EducaLegalSignupForm(SignupForm):
    full_name = forms.CharField(label="Nome Completo", required=True)
    tenant_name = forms.CharField(label="Nome da Escola", required=True)
    eua = forms.BooleanField(
        label="Concordo com a política de privacidade e os termos de uso", required=True
    )

    field_order = ["full_name", "tenant_name", "email", "password1", "password2", "eua"]

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
        tenant = Tenant.objects.create(
            name=self.cleaned_data.get("tenant_name"),
            subdomain_prefix=None,
            use_esignature=False,
            use_ged=False,
            eua_agreement=self.cleaned_data.get("eua"),
        )
        tenant.save()
        tenant_ged_data = TenantGedData.objects.create(
            tenant=tenant,
            url="",
            token="",
            database="",
            database_user="",
            database_user_password="",
            database_host="",
            database_port="",
            storage_secret_key="",
            storage_bucket_name="",
            storage_default_acl="",
            storage_endpoint_url="",
            storage_region_name=""
        )
        tenant_ged_data.save()
        tenant_esignatura_data = TenantESignatureData.objects.create(
            tenant=tenant,
            provider="",
            private_key="",
            client_id="",
            impersonated_user_guid="",
            test_mode=True
        )
        tenant_esignatura_data.save()
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
