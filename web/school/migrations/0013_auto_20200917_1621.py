# Generated by Django 3.1.1 on 2020-09-17 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0012_auto_20200810_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Logo'),
        ),
    ]
