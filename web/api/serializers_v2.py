from rest_framework import serializers

from billing.models import Plan
from document.models import Document, Envelope, Signer
from interview.models import Interview
from interview.util import get_interview_link as util_get_interview_link
from school.models import School, SchoolUnit
from tenant.models import Tenant, TenantGedData, ESignatureApp
from users.models import CustomUser


class ESignatureAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = ESignatureApp
        ref_name = "ESignatureApp v2"
        # Nao eviamos os campos de chave privada, id do usuario, etc, uma vez que envia-los apresentaria risco de seguranca
        # e eles nao sao usados no front
        fields = ["id", "provider", "test_mode"]


class InterviewSerializer(serializers.ModelSerializer):
    interview_link = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        ref_name = "Interview v2"
        fields = [
            "id",
            "name",
            "version",
            "date_available",
            "description",
            "language",
            "custom_file_name",
            "base_url",
            "is_generic",
            "is_freemium",
            "use_bulk_interview",
            "yaml_name",
            "document_type",
            "interview_server_config",
            "interview_link",
        ]

    def get_interview_link(self, obj):
        return util_get_interview_link(self.context["request"], obj.id)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = "Plan v2"
        model = Plan
        fields = "__all__"


class TenantSerializer(serializers.ModelSerializer):
    esignature_app = ESignatureAppSerializer(many=False, read_only=True)
    plan = PlanSerializer(many=False, read_only=True)

    class Meta:
        model = Tenant
        ref_name = "Tenant v2"
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    interview_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    class Meta:
        model = Document
        ref_name = "Document v2"
        fields = [
            "tenant",
            "doc_uuid",
            "name",
            "interview",
            "interview_name",
            "school",
            "school_name",
            "created_date",
            "altered_date",
            "status",
            "description",
        ]

    def get_interview_name(self, obj):
        return obj.interview.name if obj.interview else ""

    def get_school_name(self, obj):
        return obj.school.name if obj.school else ""


class EnvelopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envelope
        ref_name = "Envelope V2"
        fields = "__all__"


class SignerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signer
        ref_name = "Signer V2"
        fields = "__all__"


class DocumentDetailSerializer(serializers.ModelSerializer):
    interview_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    signers = serializers.SerializerMethodField()
    envelope = EnvelopeSerializer()

    class Meta:
        model = Document
        ref_name = "Document v2"
        fields = "__all__"

    def get_interview_name(self, obj):
        return obj.interview.name if obj.interview else ""

    def get_school_name(self, obj):
        return obj.school.name if obj.school else ""

    def get_signers(self, obj):
        try:
            # busca somente o último signer de cada email do documento
            signers = Signer.objects.raw(
                """select
                    s1.* 
                   from
                    document_signer s1
                   where
                    s1.document_id = {document_id} and
                    s1.created_date = (
                        select
                            max(created_date)
                        from
                            document_signer s2
                        where
                             s1.document_id = s2.document_id and 
                            s1.email = s2.email 
                ) order by s1.created_date desc;""".format(
                    document_id=obj.id
                )
            )
        except:
            return None
        else:
            signers = list(signers)
            # signer_statuses = list()
            signer_serialized_list = list()
            for signer in signers:
                # signer_statuses.append(signer.status)
                signer_serialized_list.append(SignerSerializer(signer).data)
            return signer_serialized_list


class SchoolSerializer(serializers.ModelSerializer):
    school_units = serializers.StringRelatedField(many=True)

    class Meta:
        model = School
        ref_name = "School v2"
        fields = "__all__"


class SchoolUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolUnit
        ref_name = "SchoolUnit v2"
        fields = "__all__"


class TenantGedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantGedData
        ref_name = "Tenant Ged Data v2"
        fields = ["tenant", "url", "token"]


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        ref_name = "User v2"
        fields = [
            "id",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "tenant",
            "groups",
            "user_permissions",
            "tenant_name",
        ]

    def get_tenant_name(self, obj):
        return obj.tenant.name if obj.tenant else ""
