from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from tenant.models import TenantAwareModel


class CustomUser(AbstractUser, TenantAwareModel):
    pass
