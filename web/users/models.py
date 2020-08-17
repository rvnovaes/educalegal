from django.db import models
from graphql_jwt.signals import token_issued
from django.dispatch import receiver
from django.contrib.auth import authenticate, login


from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from tenant.models import TenantAwareModel


class CustomUser(AbstractUser, TenantAwareModel):
    force_password_change = models.BooleanField(
        default=False, verbose_name="Obriga a trocar a senha",
        help_text="Obriga a trocar a senha no próximo login.")


@receiver(token_issued)
def login_user_after_token_issued_(sender, **kwargs):
    login(kwargs.get("request"), kwargs.get("user"))
    print("SINAL")