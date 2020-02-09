from rest_framework import generics

from tenant.models import Tenant
from .serializers import TenantSerializer


class TenantAPIViewList(generics.ListAPIView):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class TenantAPIViewDetail(generics.ListAPIView):
    serializer_class = TenantSerializer

    def get_queryset(self):
        uuid = self.kwargs['unique_id']
        return Tenant.objects.filter(unique_id=uuid)
