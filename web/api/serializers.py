from rest_framework import serializers

from document.models import Document, DocumentESignatureLog
from interview.models import Interview
from school.models import School
from tenant.models import Tenant, TenantGedData, TenantESignatureData


class DocumentESignatureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentESignatureLog
        fields = "__all__"


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


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = "__all__"


class TenantGedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantGedData
        fields = "__all__"


class TenantESignatureDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantESignatureData
        fields = "__all__"
