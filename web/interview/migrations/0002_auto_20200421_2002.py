# Generated by Django 3.0.5 on 2020-04-21 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0002_auto_20200421_2002'),
        ('interview', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='is_freemium',
            field=models.BooleanField(default=False, verbose_name='É Freemium?'),
        ),
        migrations.AlterField(
            model_name='interview',
            name='tenants',
            field=models.ManyToManyField(to='tenant.Tenant'),
        ),
    ]
