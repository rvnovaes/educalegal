from collections import OrderedDict
from operator import itemgetter
from rest_framework import serializers
from validator_collection_br import validators_br

from django.contrib.auth.password_validation import validate_password

from billing.models import Plan
from document.models import Document, Envelope, Signer
from interview.models import Interview, InterviewDocumentType
from interview.util import get_interview_link as util_get_interview_link
from school.models import School, SchoolUnit, Signatory, Grade, SignatoryKind
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


class DocumentTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewDocumentType
        ref_name = "Document Types v2"
        fields = "__all__"


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
    docx_file = serializers.SerializerMethodField()
    signers = serializers.SerializerMethodField()
    related_documents = serializers.SerializerMethodField()

    # https://www.django-rest-framework.org/api-guide/fields/#jsonfield
    # binary=True para nao serializar dicionario como string
    recipients = serializers.JSONField(binary=True)
    document_data = serializers.JSONField(binary=True)

    envelope = EnvelopeSerializer()

    class Meta:
        model = Document
        ref_name = "Document v2"
        fields = "__all__"

    def get_interview_name(self, obj):
        return obj.interview.name if obj.interview else ""

    def get_school_name(self, obj):
        return obj.school.name if obj.school else ""

    def get_docx_file(self, obj):
        docx_file = obj.get_docx_file()
        if docx_file:
            ged_link = docx_file.ged_link
            name = docx_file.name
            doc_uuid = docx_file.doc_uuid

            docx_file_data = {
                "url": ged_link,
                "name": name,
                "doc_uuid": doc_uuid
            }
        else:
            # minuta generica nao tem docx, por exemplo
            docx_file_data = None

        return docx_file_data

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

    def get_related_documents(self, obj):
        related_documents = Document.objects.filter(parent_id=obj.id)
        related_documents = list(related_documents)
        related_document_serialized_list = list()
        for related_document in related_documents:
            related_document_serialized_list.append(DocumentSerializer(related_document).data)
        if len(related_document_serialized_list) > 0:
            return related_document_serialized_list
        else:
            return None


class SchoolUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolUnit
        ref_name = "SchoolUnit v2"
        fields = "__all__"


class SignatorySerializer(serializers.ModelSerializer):
    kind_name = serializers.SerializerMethodField()

    def validate_name(self, data):
        try:
            validators_br.person_full_name(data)
        except Exception as e:
            raise serializers.ValidationError(str(e))
        return data

    class Meta:
        model = Signatory
        ref_name = "Signatory v2"
        fields = "__all__"

    def get_kind_name(self, obj):
        kind_name = 'Testemunhaaa'
        names = [item.name for item in SignatoryKind]
        if obj.kind in names:
            kind_name = SignatoryKind[obj.kind].value
        return kind_name


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        ref_name = "Grade v2"
        fields = "__all__"


# https://www.django-rest-framework.org/api-guide/serializers/#dealing-with-nested-objects
class SchoolSerializer(serializers.ModelSerializer):
    unit = serializers.CharField(allow_blank=True)
    school_units = SchoolUnitSerializer(many=True, read_only=True)
    signatories = SignatorySerializer(many=True, read_only=True)

    class Meta:
        model = School
        ref_name = "School v2"
        exclude = ('logo', )


class TenantGedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantGedData
        ref_name = "Tenant Ged Data v2"
        fields = ["tenant", "url", "token"]


class UserSerializer(serializers.ModelSerializer):
    tenant_name = serializers.SerializerMethodField()
    tenant_use_ged = serializers.SerializerMethodField()
    schools_count = serializers.SerializerMethodField()

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
            "tenant_use_ged",
            "schools_count",
            "force_password_change"
        ]

    def get_tenant_name(self, obj):
        return obj.tenant.name if obj.tenant else ""

    def get_tenant_use_ged(self, obj):
        return obj.tenant.plan.use_ged if obj.tenant else ""

    def get_schools_count(self, obj):
        return School.objects.filter(tenant=obj.tenant).count()


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value
