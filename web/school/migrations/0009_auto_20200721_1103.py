# Generated by Django 3.0.8 on 2020-07-21 14:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0008_auto_20200623_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolunit',
            name='school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='school_units', to='school.School', verbose_name='Unidade Escolar'),
        ),
    ]
