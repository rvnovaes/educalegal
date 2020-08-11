from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("school", "0009_auto_20200721_1103"),
    ]
    operations = [
        migrations.AddField(
            model_name='school',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Criação"),
        ),
        migrations.RunSQL("""update
  school_school s
set
  created_date = t.created_date
from
  tenant_tenant t
where
  s.tenant_id = t.id;"""),
        migrations.AlterField(
            model_name='school',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, blank=True, verbose_name="Criação"),
        ),
    ]