# Generated by Django 3.0.8 on 2020-07-30 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0006_auto_20200602_1339'),
        ('document', '0016_auto_20200721_0921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='envelope_id',
        ),
        migrations.RemoveField(
            model_name='document',
            name='signing_provider',
        ),
        migrations.AddField(
            model_name='document',
            name='envelope_id_old',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Id do Envelope'),
        ),
        migrations.CreateModel(
            name='Signer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Criação')),
                ('name', models.CharField(max_length=256, verbose_name='Nome')),
                ('email', models.EmailField(max_length=256, verbose_name='E-mail')),
                ('type', models.CharField(max_length=256, verbose_name='Tipo')),
                ('status', models.CharField(max_length=256, verbose_name='Status')),
                ('sent_date', models.DateTimeField(blank=True, null=True, verbose_name='Envio')),
                ('pdf_filenames', models.TextField(blank=True, verbose_name='PDFs')),
                ('envelope_log_id', models.IntegerField(blank=True, null=True, verbose_name='envelope_log_id')),
                ('signer_log_id', models.IntegerField(blank=True, null=True, verbose_name='signer_log_id')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signers', to='document.Document', verbose_name='Documento')),
                ('tenant', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tenant.Tenant')),
            ],
            options={
                'verbose_name': 'Signatário',
                'verbose_name_plural': 'Signatários',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='Envelope',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Criação')),
                ('altered_date', models.DateTimeField(auto_now=True, verbose_name='Alteração')),
                ('identifier', models.CharField(max_length=256, verbose_name='ID')),
                ('status', models.CharField(max_length=256, verbose_name='Status')),
                ('envelope_created_date', models.DateTimeField(verbose_name='Criação do envelope')),
                ('sent_date', models.DateTimeField(null=True, verbose_name='Envio')),
                ('status_update_date', models.DateTimeField(null=True, verbose_name='Alteração do status')),
                ('signing_provider', models.CharField(blank=True, default='', max_length=256, verbose_name='Provedor')),
                ('envelope_log_id', models.IntegerField(blank=True, null=True, verbose_name='envelope_log_id')),
                ('tenant', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='tenant.Tenant')),
            ],
            options={
                'verbose_name': 'Envelope',
                'verbose_name_plural': 'Envelopes',
                'ordering': ['-envelope_created_date'],
            },
        ),
        migrations.AddField(
            model_name='document',
            name='envelope',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='document.Envelope', verbose_name='Envelope'),
        ),
        migrations.AddIndex(
            model_name='signer',
            index=models.Index(fields=['name'], name='document_si_name_dba128_idx'),
        ),
        migrations.AddIndex(
            model_name='signer',
            index=models.Index(fields=['email'], name='document_si_email_ca7735_idx'),
        ),
        migrations.AddIndex(
            model_name='signer',
            index=models.Index(fields=['status'], name='document_si_status_699c46_idx'),
        ),
        migrations.AddIndex(
            model_name='envelope',
            index=models.Index(fields=['identifier'], name='document_en_identif_a4917e_idx'),
        ),
        migrations.AddIndex(
            model_name='envelope',
            index=models.Index(fields=['status'], name='document_en_status_4aad6c_idx'),
        ),
    ]
