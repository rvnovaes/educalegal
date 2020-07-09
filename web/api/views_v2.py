import logging

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError


from billing.models import *
from document.models import *
from interview.models import *
from school.models import *
from tenant.models import *

from .serializers_v2 import (
    PlanSerializer,
    DocumentSerializer,
    InterviewSerializer,
    SchoolSerializer,
    TenantSerializer,
    TenantGedDataSerializer
)

logger = logging.getLogger(__name__)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna dados dos planos disponíveis para contratação. Disponível apenas para administradores.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def list(self, request, *args, **kwargs):
        """
        Lista todos os documentos do Cliente (tenant) ao qual o usuário está associado.
        """
        tenant_id = request.user.tenant.id
        queryset = self.queryset.filter(tenant_id=tenant_id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Atualiza parcialmente um documento já existente.
        400 BAD REQUEST: O uuid do documento (e.g.: "doc_uuid"="732be220-afe5-4c45-8d36-xxxxxxxxxxxx) é obrigatório.
        404 NOT FOUND: Se o documento (doc_uuid) não existir ou se o usuário que faz a requisição não pertencer ao cliente
        (tenant) dono do doc_uiid.
        """
        try:
            doc_uuid = request.data["doc_uuid"]
        except KeyError as e:
            message = "O campo {field_name} é obrigatório para essa requisição".format(field_name=str(e))
            logger.info(message)
            raise ValidationError(message)
        else:
            tenant_id = request.user.tenant.id
            instance = get_object_or_404(self.queryset, doc_uuid=doc_uuid, tenant=tenant_id)
            logger.info("Atualizando o documento {doc_uuid}".format(doc_uuid=str(doc_uuid)))
            serializer = self.serializer_class(instance, data=request.data, partial=True, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a lista de todas as entrevistas.
    """
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAdminUser]


class TenantSchoolViewSet(viewsets.ViewSet):
    def list(self, request, pk=None):
        queryset = School.objects.filter(tenant=pk)
        serializer = SchoolSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, spk=None):
        queryset = School.objects.all()
        school = get_object_or_404(queryset, id=spk, tenant=pk)
        serializer = SchoolSerializer(school)
        return Response(serializer.data)


class TenantInterviewViewSet(viewsets.ViewSet):
    def list(self, request, pk=None):
        queryset = Interview.objects.filter(tenants=pk)
        serializer = InterviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, spk=None):
        queryset = Interview.objects.all()
        interview = get_object_or_404(queryset, id=spk, tenants=pk)
        serializer = SchoolSerializer(interview)
        return Response(serializer.data)


class TenantDocumentViewSet(viewsets.ViewSet):
    def list(self, request, pk=None):
        queryset = Document.objects.filter(tenant=pk)
        serializer = DocumentSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, spk=None):
        queryset = Document.objects.all()
        interview = get_object_or_404(queryset, id=spk, tenant=pk)
        serializer = DocumentSerializer(interview)
        return Response(serializer.data)


class TenantPlanView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        """
        Retorna dados do plano do Cliente (tenant) especificado em {id}
        """
        tenant = get_object_or_404(Tenant, pk=pk)
        plan = get_object_or_404(Plan, pk=tenant.plan.pk)
        serializer = PlanSerializer(plan)
        return Response(serializer.data)


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a listagem de clientes (tenants) ou o cliente específico.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class TenantGedDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TenantGedDataSerializer

    def get_queryset(self):
        return TenantGedData.objects.filter(tenant=self.kwargs["pk"])