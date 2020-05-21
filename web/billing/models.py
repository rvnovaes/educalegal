from djmoney.models.fields import MoneyField
from django.db import models
from enum import Enum


class PlanType(Enum):
    ESSENTIAL = "Essential"
    STANDARD = "Standard"
    PREMIUM = "Premium"
    CORPORATE = "Corporate"

    def __str__(self):
        return str(self.value.lower())

    @classmethod
    def choices(cls):
        return [(x.name, x.value) for x in cls]


class Plan(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Plano")
    value = MoneyField(
        max_digits=14,
        decimal_places=2,
        default=0,
        default_currency="BRL",
        verbose_name="Valor Mensal",
    )
    document_limit = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Limite de Documentos",
        help_text="Para documentos ilimitados, deixar o campo em branco ou preencher com 0 (zero).",
    )
    plan_type = models.CharField(
        verbose_name="Tipo de Plano",
        max_length=30,
        choices=PlanType.choices(),
        default=PlanType.ESSENTIAL,
    )
    use_esignature = models.BooleanField(
        default=False, verbose_name="Usa assinatura eletrônica"
    )
    use_ged = models.BooleanField(
        default=False, verbose_name="Usa gestão eletrônica de documentos"
    )
    use_bulk_interview = models.BooleanField(
        default=False, verbose_name="Usa geração em lote"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return self.name
