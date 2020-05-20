# Generated by Django 3.0.6 on 2020-05-20 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_interview', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bulkgeneration',
            name='source_file',
        ),
        migrations.AddField(
            model_name='bulkgeneration',
            name='mongo_db_collection_name',
            field=models.CharField(default='nenhum', max_length=1024, verbose_name='Coleção de Documentos no Mongo'),
            preserve_default=False,
        ),
    ]
