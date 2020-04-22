# Generated by Django 3.0.5 on 2020-04-21 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='eua_agreement',
            field=models.BooleanField(default=True, verbose_name='Concordo com os termos de uso'),
        ),
        migrations.AddField(
            model_name='tenant',
            name='use_ged',
            field=models.BooleanField(default=False, verbose_name='Usa gestão eletrônica de documentos'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='use_esignature',
            field=models.BooleanField(default=False, verbose_name='Usa assinatura eletrônica'),
        ),
    ]
