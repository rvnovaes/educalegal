from rest_framework import generics

from tenant.models import Tenant
from .serializers import TenantSerializer


class TenantAPIViewList(generics.ListAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class TenantAPIViewDetail(generics.RetrieveAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
