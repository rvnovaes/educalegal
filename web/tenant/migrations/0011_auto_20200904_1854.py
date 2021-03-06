# Generated by Django 3.0.9 on 2020-09-04 21:54

from django.db import migrations, models

update_name = """
update tenant_esignatureappsignerkey 
set name = email;"""


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0010_tenant_esignature_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='esignatureappsignerkey',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Nome'),
        ),
        migrations.AlterUniqueTogether(
            name='esignatureappsignerkey',
            unique_together={('email', 'name', 'tenant', 'esignature_app')},
        ),
        migrations.RunSQL(update_name),
        migrations.AlterField(
            model_name='esignatureappsignerkey',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Nome'),
        ),
    ]
