from rest_framework import serializers

from document.models import Document
from interview.models import Interview
from school.models import School
from tenant.models import Tenant


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = "__all__"


class SchoolSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    state = serializers.StringRelatedField()
    country = serializers.StringRelatedField()
    class Meta:
        model = School
        fields = "__all__"


class TenantGEDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["name", "ged_url", "ged_token"]

