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

    def resolve_all_documents(self, info):
        tenant = info.context.user.tenant
        return Document.objects.filter(tenant=tenant)

    # def resolve_all_schools(self, info):
    #     tenant = info.context.user.tenant
    #     return School.objects.filter(tenant=tenant)

    @graphene.resolve_only_args
    def resolve_all_schools(self):
        return School.objects.all()


schema = graphene.Schema(query=Query)
