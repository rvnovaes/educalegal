from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("school", "0009_auto_20200721_1103"),
    ]

    operations = [
        migrations.AddField(
            model_name='school',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name="Criação"),
        ),
        migrations.RunSQL("""update 
  school_school e  
set 
  created_date = d.created_date
from 
  tenant_tenant d
where 
  e.tenant_id = d.id;""")
    ]