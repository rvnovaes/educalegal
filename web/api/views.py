from rest_framework import generics
from rest_framework import viewsets

from tenant.models import Tenant
from school.models import School
from .serializers import SchoolSerializer, TenantGEDSerializer


class TenantGEDViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list or retrieves a tenant
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantGEDSerializer


class TenantSchoolsAPIViewList(generics.ListAPIView):
    serializer_class = SchoolSerializer

    def get_queryset(self):
        tid = self.kwargs["pk"]
        return School.objects.filter(tenant=tid)


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

