# Generated by Django 3.0.9 on 2020-08-24 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0011_auto_20200904_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='webhook_production',
            field=models.URLField(blank=True, max_length=255, verbose_name='Webhook de produção'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='webhook_sandbox',
            field=models.URLField(blank=True, max_length=255, verbose_name='Webhook de homologação'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Nome'),
        ),
    ]
