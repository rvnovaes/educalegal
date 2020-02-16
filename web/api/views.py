from rest_framework import generics
from rest_framework import viewsets

from document.models import Document
from interview.models import Interview
from school.models import School
from tenant.models import Tenant

from .serializers import DocumentSerializer, InterviewSerializer, SchoolSerializer, TenantGEDSerializer


class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class TenantGEDViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list or retrieves a tenant. The serializer only returns a subset of fields necessary to run the
    interview so not to expose sensitive data.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantGEDSerializer


class TenantSchoolsViewList(generics.ListAPIView):
    serializer_class = SchoolSerializer

    def get_queryset(self):
        tid = self.kwargs["pk"]
        return School.objects.filter(tenant=tid)
