from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_analyst = models.BooleanField(
        _('Analyst'),
        default=False,
        help_text=_(
            'Analyst is the lowest level on hierarchy of an organization.'))
    is_manager = models.BooleanField(
        _('Manager'),
        default=False,
        help_text=_(
            'A manager is in charge of a business unit.'
        ))
    is_administrator = models.BooleanField(
        _('Administrator'),
        default=False,
        help_text=_(
            'Administrator of the organization. Not to be confused with a Superuser.'
        ))
