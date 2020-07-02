import django_filters

from .models import Document, School


# https://django-filter.readthedocs.io/en/stable/ref/filters.html#choicefilter
STATUS_CHOICES = (
    ("rascunho", "rascunho"),
    ("criado", "criado"),
    ("inserido no GED", "inserido no GED"),
    ("enviado", "enviado"),
    ("finalizado", "finalizado"),
    ("rascunho - em lote", "rascunho - em lote")
)


# https://django-filter.readthedocs.io/en/stable/guide/usage.html#filtering-the-related-queryset-for-modelchoicefilter
def schools(request):
    if request is None:
        return Document.objects.none()

    tenant = request.user.tenant
    return School.objects.filter(tenant=tenant)


class DocumentFilter(django_filters.FilterSet):
    school = django_filters.ModelChoiceFilter(queryset=schools, label="Escola")
    status = django_filters.ChoiceFilter(choices=STATUS_CHOICES)

    class Meta:
        model = Document
        fields = ["school", "status"]
