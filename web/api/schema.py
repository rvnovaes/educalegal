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

class SchoolMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        id = graphene.ID()
        name = graphene.String()

    # The class attributes define the response of the mutation
    school = graphene.Field(SchoolType)

    def mutate(self, info, id, name):
        school = School.objects.get(pk=id)
        school.name = name
        school.save()
        return SchoolMutation(school=school)


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


class Mutation(graphene.ObjectType):
    update_school = SchoolMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
