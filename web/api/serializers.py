from rest_framework import serializers

from billing.models import Plan
from document.models import Document, Envelope, Signer
from interview.models import Interview
from school.models import School
from tenant.models import Tenant, TenantGedData, ESignatureApp, ESignatureAppSignerKey


class DocumentSerializer(serializers.ModelSerializer):
    interview_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        ref_name = "Document v1"
        fields = "__all__"

    def get_interview_name(self, obj):
        return obj.interview.name if obj.interview else ''

    def get_school_name(self, obj):
        return obj.school.name if obj.school else ''


class EnvelopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envelope
        ref_name = "Envelope v1"
        fields = "__all__"


class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        ref_name = "Signer v1"
        fields = "__all__"


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        ref_name = "Interview v1"
        fields = "__all__"


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        ref_name = "Plan v1"
        fields = "__all__"


class SchoolSerializer(serializers.ModelSerializer):
    city = serializers.StringRelatedField()
    state = serializers.StringRelatedField()
    country = serializers.StringRelatedField()
    school_units = serializers.StringRelatedField(many=True)
    signing_people = serializers.StringRelatedField(many=True)

    class Meta:
        model = School
        ref_name = "School v1"
        fields = "__all__"


class TenantGedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantGedData
        ref_name = "TenantGedData v1"
        fields = "__all__"


class ESignatureAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESignatureApp
        ref_name = "ESignatureApp v1"
        fields = "__all__"


class TenantSerializer(serializers.ModelSerializer):
    esignature_app = ESignatureAppSerializer(many=False, read_only=True)

    class Meta:
        model = Tenant
        ref_name = "Tenant v1"
        fields = "__all__"


class ESignatureAppSignerKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ESignatureAppSignerKey
        ref_name = "ESignatureAppSignerKey v1"
        fields = "__all__"
