import django_filters

from .models import Interview


class InterviewFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Buscar pelo nome")

    class Meta:
        model = Interview
        fields = ["name"]
