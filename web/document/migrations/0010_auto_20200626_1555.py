# Generated by Django 3.0.7 on 2020-06-26 18:55

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_auto_20200614_1704'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTaskView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='Nome')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Criação')),
                ('altered_date', models.DateTimeField(auto_now=True, verbose_name='Alteração')),
                ('signing_provider', models.CharField(default='', max_length=256, verbose_name='Provedor')),
                ('envelope_id', models.CharField(default='', max_length=256, verbose_name='Id do Envelope')),
                ('document_status', models.CharField(default='', max_length=256, verbose_name='Status do Documento')),
                ('ged_id', models.CharField(default='', max_length=128, verbose_name='ID do Documento no GED')),
                ('ged_link', models.CharField(default='', max_length=256, verbose_name='Link')),
                ('ged_uuid', models.CharField(default='', help_text='UUID do documento. UUID = Universally Unique ID.', max_length=256, verbose_name='UUID')),
                ('description', models.TextField(default='', verbose_name='Descrição')),
                ('document_data', django.contrib.postgres.fields.jsonb.JSONField(null=True, verbose_name='Dados do Documento')),
                ('doc_uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')),
                ('task_create_document', models.CharField(default='', max_length=256, verbose_name='Task de criação de documento')),
                ('task_submit_to_esignature', models.CharField(default='', max_length=256, verbose_name='Task de assinatura')),
                ('submit_to_esignature', models.BooleanField(default=False, verbose_name='Enviar para assinatura eletrônica?')),
                ('send_email', models.BooleanField(default=False, verbose_name='Enviar por e-mail?')),
                ('mongo_uuid', models.CharField(default='', max_length=256, verbose_name='UUID do Mongo')),
                ('task_name', models.CharField(max_length=255, null=True, verbose_name='Nome da Task')),
                ('task_status', models.CharField(max_length=50, verbose_name='Status da Task')),
                ('task_created_date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Criação da Task')),
                ('task_done_date', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Término da Task')),
                ('traceback', models.TextField(blank=True, null=True, verbose_name='Traceback')),
            ],
            options={
                'db_table': 'document_task',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='document',
            name='send_email',
            field=models.BooleanField(default=False, verbose_name='Enviar por e-mail?'),
        ),
    ]