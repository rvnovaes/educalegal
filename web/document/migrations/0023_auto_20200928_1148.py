# Generated by Django 3.1.1 on 2020-09-28 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0022_auto_20200915_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_documents', to='document.document'),
        ),
    ]
