from djmoney.models.fields import MoneyField
from django.db import models


class Plan(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Plano")
    value = MoneyField(
        max_digits=14,
        decimal_places=2,
        default=0,
        default_currency="BRL",
        verbose_name="Valor Mensal",
    )
    document_limit = models.IntegerField(null=True, blank=True, verbose_name="Limite de Documentos")

    class Meta:
        ordering = ["name"]
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return self.name
