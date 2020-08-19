from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from tenant.models import TenantAwareModel


class CustomUser(AbstractUser, TenantAwareModel):
    force_password_change = models.BooleanField(
        default=False, verbose_name="Obriga a trocar a senha",
        help_text="Obriga a trocar a senha no próximo login.")
