from graphene_django import DjangoObjectType
import graphene

from school.models import School


class SchoolType(DjangoObjectType):
    class Meta:
        model = School


class Query(graphene.ObjectType):
    schools = graphene.List(SchoolType)

    @graphene.resolve_only_args
    def resolve_schools(self):
        return School.objects.all()


schema = graphene.Schema(query=Query)
