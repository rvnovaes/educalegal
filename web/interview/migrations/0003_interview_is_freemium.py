# Generated by Django 3.0.5 on 2020-04-20 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0002_auto_20200420_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='is_freemium',
            field=models.BooleanField(default=False, verbose_name='É Freemium?'),
        ),
    ]
