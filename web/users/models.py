from django.db import models
from django.dispatch import receiver
from django.contrib.auth import authenticate, login

from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from tenant.models import TenantAwareModel


class CustomUser(AbstractUser, TenantAwareModel):
    force_password_change = models.BooleanField(
        default=False, verbose_name="Obriga a trocar a senha",
        help_text="Obriga a trocar a senha no próximo login.")
    temp_key = models.CharField(max_length=256, default="", null=True, verbose_name="Chave temporária para reset de senha")
    temp_key_created_date = models.DateTimeField(auto_now=True, verbose_name="Criação da chave temporária",
                                                 blank=True)


