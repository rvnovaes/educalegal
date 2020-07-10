import logging
import re

from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import status

from validator_collection import checkers, validators


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

UUID = "([a-z]|[0-9]){8}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){12}"


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

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera o documento com base em um identificador (identifier).

        O identificador, neste método, pode ser uma id (inteiro) ou doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        Somente documentos que pertencem ao cliente (tenant) ao qual o usuário está vinculado são recuperados.

        400 BAD REQUEST: Se for feita uma requisição e o valor informado não for um id numérico (inteiro) ou não for um uuid válido, mno formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            => "O doc_uuid ou o id do documento não são valores válidos."

        404 NOT FOUND: Se o documento (id ou doc_uuid) não existir ou se o documento requisitado não pertencer ao cliente
        (tenant) ao qual o usuário da requisição está vinculado.
        """
        tenant_id = request.user.tenant.id
        identifier = kwargs["identifier"]
        # Pode ser passada a id ou o doc_uuid.
        if checkers.is_integer(identifier, coerce_value=True):
            instance = get_object_or_404(self.queryset, pk=identifier, tenant=tenant_id)
        elif checkers.is_uuid(identifier):
            instance = get_object_or_404(self.queryset, doc_uuid=identifier, tenant=tenant_id)
        else:
            message = "O doc_uuid ou o id do documento não é um valor válido."
            logger.info(message)
            raise ValidationError(message)

        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lista todos os documentos do cliente (tenant).

        Somente documetos que pertencem ao cliente ao qual o usuário está associado são listados.
        """
        tenant_id = request.user.tenant.id
        queryset = self.queryset.filter(tenant_id=tenant_id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Cria um novo documento.

        400 BAD REQUEST: Se for tentada a criação de um documento em um cliente (tenant) distinto daquele ao qual o usuário está vinculado.
            => "Somente é permitida a criação de documentos no seu cliente (tenant)."
        """
        tenant_id = request.user.tenant.id
        if "tenant" in request.data:
            if tenant_id != int(request.data["tenant"]):
                message = "Somente é permitida a criação de documentos no seu cliente (tenant)."
                logger.info(message)
                raise ValidationError(message)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        """
        Atualiza parcialmente um documento já existente.

        Atualização requer como parâmetro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: O payload deve sempre conter o doc_uuid para essa operação. Não é possível atualizar (PATCH) um
        documento com base no seu ID. => "O campo doc_uuid é obrigatório para essa requisição."

        400 BAD REQUEST: Tentativa de alteração de documento que não pertence ao cliente (tenant) ao qual o usuário está vinculado
            => "Não é permitido alterar o cliente (tenant) proprietário do documento."

        400 BAD REQUEST: Se o campo doc_uuid não for válido
            => "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        404 NOT FOUND: Se o documento (doc_uuid) não existir ou se o documento requisitado não pertencer ao cliente
        (tenant) ao qual o usuário da requisição está vinculado.
        """
        try:
            doc_uuid = request.data["doc_uuid"]
        except KeyError:
            message = "O campo doc_uuid é obrigatório para essa requisição."
            logger.info(message)
            raise ValidationError(message)
        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        else:
            tenant_id = request.user.tenant.id
            instance = get_object_or_404(self.queryset, doc_uuid=doc_uuid, tenant=tenant_id)

            if "tenant" in request.data:
                if tenant_id != int(request.data["tenant"]):
                    message = "Não é permitido alterar o cliente (tenant) proprietário do documento."
                    logger.info(message)
                    raise ValidationError(message)

            logger.info("Atualizando o documento {doc_uuid}".format(doc_uuid=str(doc_uuid)))
            serializer = self.serializer_class(instance, data=request.data, partial=True, context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Exclui o documento.

        Exclusão requer como parâmetro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Se o campo doc_uuid não for válido:
            => "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        403 FORBIDDEN: Tentativa de exlusão de documento por usuário sem permissões (is_staff = True).
            => "Somente usuários administradores podem excluir documentos."

        404 NOT FOUND: Se o documento (doc_uuid) não existir ou se o documento requisitado não pertencer ao cliente
        (tenant) ao qual o usuário da requisição está vinculado.
        """
        doc_uuid = kwargs["identifier"]
        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        else:
            user = request.user
            if user.is_staff:
                tenant_id = request.user.tenant.id
                instance = get_object_or_404(self.queryset, doc_uuid=doc_uuid, tenant=tenant_id)
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                message = "Somente usuários administradores podem excluir documentos."
                logger.info(message)
                raise PermissionDenied(message)


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