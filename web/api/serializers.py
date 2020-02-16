from rest_framework import serializers

from document.models import Document
from school.models import School
from tenant.models import Tenant


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


class TenantGEDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["name", "ged_url", "ged_token"]

