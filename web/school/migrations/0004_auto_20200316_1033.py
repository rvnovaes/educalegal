# Generated by Django 3.0.4 on 2020-03-16 13:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("school", "0003_auto_20200311_1125"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="city",
            options={
                "ordering": ("name",),
                "verbose_name": "Cidade",
                "verbose_name_plural": "Cidades",
            },
        ),
    ]
