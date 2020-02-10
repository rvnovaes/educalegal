from rest_framework import generics
from rest_framework import viewsets

from tenant.models import Tenant
from school.models import School
from .serializers import SchoolSerializer, TenantSerializer


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class TenantSchoolsAPIViewList(generics.ListAPIView):
    serializer_class = SchoolSerializer

    def get_queryset(self):
        tid = self.kwargs["pk"]
        return School.objects.filter(tenant=tid)


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

