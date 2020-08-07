# Generated by Django 3.0.8 on 2020-07-28 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20200420_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='force_password_change',
            field=models.BooleanField(default=False, help_text='Obriga a trocar a senha no próximo login.', verbose_name='Obriga a trocar a senha'),
        ),
    ]
