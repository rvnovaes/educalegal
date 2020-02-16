from rest_framework import generics
from rest_framework import viewsets

from document.models import Document
from school.models import School
from tenant.models import Tenant

from .serializers import DocumentSerializer, SchoolSerializer, TenantGEDSerializer


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


class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request,*args, **kwargs)


