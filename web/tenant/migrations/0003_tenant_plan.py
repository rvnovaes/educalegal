# Generated by Django 3.0.6 on 2020-05-07 21:04

from django.db import migrations, models
import django.db.models.deletion


def create_essential_plan(apps, schema_editor):
    # apps.get_model("<nome do app>", "<nome do model>")
    Plan = apps.get_model("billing", "Plan")
    essential_plan = Plan(
        name="Essential",
        value=0.00,
        document_limit=10)
    essential_plan.save()


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
        ('tenant', '0002_auto_20200421_2002'),
    ]

    operations = [
        migrations.RunPython(create_essential_plan),
        migrations.AddField(
            model_name='tenant',
            name='plan',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='tenants', to='billing.Plan', verbose_name='Plano'),
        ),
    ]
