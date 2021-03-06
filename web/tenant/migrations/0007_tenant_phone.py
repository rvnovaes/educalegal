# Generated by Django 3.0.9 on 2020-08-14 16:25

from django.db import migrations, models

update_phone = """update
  tenant_tenant t
set
  phone = s.phone
from
  school_school s
where
  t.id = s.tenant_id;"""


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0006_auto_20200602_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='phone',
            field=models.CharField(blank=True, max_length=50, verbose_name='Telefone'),
        ),
        migrations.RunSQL(update_phone),
    ]
