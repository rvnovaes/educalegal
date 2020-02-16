from rest_framework import serializers

from tenant.models import Tenant
from school.models import School


class TenantGEDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["name", "ged_url", "ged_token"]


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
