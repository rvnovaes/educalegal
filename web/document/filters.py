import django_filters

from .models import Document, School, DocumentStatus


# https://django-filter.readthedocs.io/en/stable/guide/usage.html#filtering-the-related-queryset-for-modelchoicefilter
def schools(request):
    if request is None:
        return Document.objects.none()

    tenant = request.user.tenant
    return School.objects.filter(tenant=tenant)


class DocumentFilter(django_filters.FilterSet):
    school = django_filters.ModelChoiceFilter(queryset=schools, label="Escola")
    status = django_filters.ChoiceFilter(choices=DocumentStatus.choices())

    class Meta:
        model = Document
        fields = ["school", "status"]
