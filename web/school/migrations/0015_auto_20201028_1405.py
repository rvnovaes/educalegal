# Generated by Django 3.1.2 on 2020-10-28 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0014_auto_20200918_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='site',
            field=models.URLField(blank=True, verbose_name='Site'),
        ),
        migrations.RemoveField(
            model_name='school',
            name='legal_nature',
        ),
        migrations.AlterField(
            model_name='school',
            name='cnpj',
            field=models.CharField(max_length=255, verbose_name='CNPJ'),
        ),
    ]
