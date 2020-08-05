import graphene
from graphene_django import DjangoObjectType, DjangoConnectionField


from document.models import Document
from school.models import School, SchoolUnit


class DocumentType(DjangoObjectType):
    class Meta:
        model = Document


class SchoolType(DjangoObjectType):
    class Meta:
        model = School


class Query(graphene.ObjectType):
    all_documents = graphene.List(DocumentType)
    all_schools = graphene.List(SchoolType)
    school = graphene.Field(SchoolType, id=graphene.Int())

    def resolve_all_documents(self, info):
        tenant = info.context.user.tenant
        return Document.objects.filter(tenant=tenant)

    # def resolve_all_schools(self, info):
    #     tenant = info.context.user.tenant
    #     return School.objects.filter(tenant=tenant)

    @graphene.resolve_only_args
    def resolve_all_schools(self):
        return School.objects.all()

    def resolve_school(self, info, **kwargs):
        id = kwargs.get('id')
        return School.objects.get(pk=id)



schema = graphene.Schema(query=Query)
