# Generated by Django 3.0.7 on 2020-06-23 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0007_auto_20200503_2303'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='school',
            options={'ordering': ['name'], 'verbose_name': 'Escola', 'verbose_name_plural': 'Escolas'},
        ),
    ]