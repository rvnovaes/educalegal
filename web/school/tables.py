import django_tables2 as tables
from django_tables2.utils import A
from .models import School


class SchoolTable(tables.Table):
    legal_name = tables.LinkColumn('school:school-detail', args=[A('pk')])

    class Meta:
        model = School
        template_name = 'django_tables2/bootstrap4.html'
        fields = ('legal_name', 'city', 'state')
