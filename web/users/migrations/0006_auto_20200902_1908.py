# Generated by Django 3.1 on 2020-09-02 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auto_20200902_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='temp_key',
            field=models.CharField(default='', max_length=256, null=True, verbose_name='Chave temporária para reset de senha'),
        ),
    ]