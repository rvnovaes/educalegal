# Generated by Django 3.0.6 on 2020-05-13 23:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0004_auto_20200513_1705'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tenant',
            name='use_esignature',
        ),
        migrations.RemoveField(
            model_name='tenant',
            name='use_ged',
        ),
    ]