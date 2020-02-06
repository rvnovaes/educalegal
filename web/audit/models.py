from django.db import models
from django.conf import settings

from tenant.models import TenantAwareModel


class Audit(TenantAwareModel):
    create_date = models.DateTimeField('Criado em', auto_now_add=True)
    create_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='%(class)s_create_user',
        verbose_name='Criado por')
    alter_date = models.DateTimeField(
        'Atualizado em', auto_now=True, blank=True, null=True)
    alter_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='%(class)s_alter_user',
        verbose_name='Alterado por')
    is_active = models.BooleanField(
        null=False, default=True, verbose_name='Ativo')

    class Meta:
        abstract = True

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()
