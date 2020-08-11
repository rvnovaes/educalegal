import graphene
from django.shortcuts import get_object_or_404
from graphene_django import DjangoObjectType, DjangoConnectionField

from document.models import Document
from school.models import School, SchoolUnit


class DocumentType(DjangoObjectType):
    class Meta:
        model = Document


class SchoolType(DjangoObjectType):
    class Meta:
        model = School


class CreateSchool(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        legal_name = graphene.String(required=True)
        legal_nature = graphene.String(required=True)
        cnpj = graphene.String(required=True)
        phone = graphene.String(required=True)
        site = graphene.String(required=True)
        email = graphene.String(required=True)
        zip = graphene.String(required=True)
        street = graphene.String(required=True)
        street_number = graphene.String(required=True)
        unit = graphene.String()
        neighborhood = graphene.String(required=True)
        city = graphene.String(required=True)
        state = graphene.String(required=True)

    # The class attributes define the response of the mutation
    school = graphene.Field(SchoolType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        school = School(**kwargs)
        school.save()
        return CreateSchool(school=school)


class UpdateSchool(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        id = graphene.ID(required=True)
        name = graphene.String()
        legal_name = graphene.String()
        legal_nature = graphene.String()
        cnpj = graphene.String()
        phone = graphene.String()
        site = graphene.String()
        email = graphene.String()
        zip = graphene.String()
        street = graphene.String()
        street_number = graphene.String()
        unit = graphene.String()
        neighborhood = graphene.String()
        city = graphene.String()
        state = graphene.String()

    # The class attributes define the response of the mutation
    school = graphene.Field(SchoolType)

    @classmethod
    def mutate(cls, root, info, **kwargs):
        school = get_object_or_404(School, pk=kwargs["id"])
        for k, v in kwargs.items():
            setattr(school, k, v)
        school.save()
        return UpdateSchool(school=school)


class DeleteSchool(graphene.Mutation):
    ok = graphene.Boolean()

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        school = get_object_or_404(School, pk=kwargs["id"])
        school.delete()
        return cls(ok=True)


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
    create_school = CreateSchool.Field()
    update_school = UpdateSchool.Field()
    delete_school = DeleteSchool.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
