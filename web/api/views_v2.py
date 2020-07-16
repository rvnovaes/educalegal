import logging
import io

from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound, APIException
from rest_framework import status
from rest_framework.decorators import api_view



from validator_collection import checkers, validators


from billing.models import *
from document.models import *
from interview.models import *
from school.models import *
from tenant.models import *
from .mayan_helpers import MayanClient

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

    200 Sucesso
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

        200 Sucesso
        """
        tenant_id = request.user.tenant.id
        queryset = self.queryset.filter(tenant_id=tenant_id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Cria um novo documento.

        Nõa é necessário informar o tenant no corpo da requisição. O sistema usa o cliente do usuário ao qual o usuário está vinculado.

        400 BAD REQUEST: Se for tentada a criação de um documento em um cliente (tenant) distinto daquele ao qual o usuário está vinculado.
            => "Somente é permitida a criação de documentos no seu cliente (tenant)."
        """
        tenant_id = request.user.tenant.id
        if "tenant" in request.data:
            if tenant_id != int(request.data["tenant"]):
                message = "Somente é permitida a criação de documentos no seu cliente (tenant)."
                logger.info(message)
                raise ValidationError(message)
        else:
            request.data["tenant"] = tenant_id
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


def validate_tenant_plan_ged(tenant):
    if not tenant.plan.use_ged:
        message = "Somente clientes cadastrados num plano que possui GED podem baixar documentos."
        logger.info(message)
        raise PermissionDenied(message)
    else:
        try:
            tenand_ged_data = TenantGedData.objects.get(tenant=tenant)
            ged_url = tenand_ged_data.url
            tenant_ged_token = tenand_ged_data.token
        except TenantGedData.DoesNotExist:
            message = "O cliente está cadastrado num plano que possui GED mas mão há GED configurado para ele."
            logger.info(message)
            raise APIException(message)

        # Aqui preferimos testar o tamanho da URL ao invés de fazer o checker.is_url, uma vez que, em ambiente de dev,
        # se usar, eg, http://ged:8000 a validação falha

        if not len(ged_url) or len(tenant_ged_token) == 0:
            message = "O GED do cliente não possui uma URL válida ou não possui token configurado"
            logger.info(message)
            raise APIException(message)

        return ged_url, tenant_ged_token


class DocumentDownloadView(APIView):

    queryset = Document.objects.all()

    def get(self, request, identifier):

        """
        Baixa o documento do GED.

        Download requer como parâmetro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Se o campo doc_uuid não for válido:
            => "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        403 FORBIDDEN: O cliente deve possuir GED para poder baixar documentos
            => "Somente clientes cadastrados num plano que possui GED podem baixar documentos."

        404 NOT FOUND: Se o documento (doc_uuid) não existir ou se o documento requisitado não pertencer ao cliente
            (tenant) ao qual o usuário da requisição está vinculado.

        404 NOT FOUND: Se o documento existir no Educa Legal mas não for encontrado no GED. Pode ocorrer de um usuário excluir o documento diretamente no GED.
            => "O documento não foi encontrado no GED. Possivelmente ele foi excluído diretamente no GED sem utilização do app Educa Legal.  Verifique a lixeira no GED."

        500 INTERNAL SERVER ERROR: Se o cliente estiver num plano que possui GED mas não há GED configurado para ele.
            => "O cliente está cadastrado num plano que possui GED mas mão há GED configurado para ele."

        500 INTERNAL SERVER ERROR: Se há GED cadastrado para o cliente mas não há URL ou TOKEN cadastrados.
            => "O GED do cliente não possui uma URL válida ou não possui token configurado"

        500 INTERNAL SERVER ERROR: Se houver problemas na conexão com o GED (não está disponível, por exemplo).
            => "Failed to establish a new connection: [Errno 111] Connection refused"


        :param request: HttpRequest
        :param identifier: id ou doc_uui do documento no Educa Legal
        :return: O arquivo do documento no GED
        """
        tenant = request.user.tenant

        if not checkers.is_uuid(identifier):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        elif checkers.is_uuid(identifier):
            document = get_object_or_404(self.queryset, doc_uuid=identifier, tenant=tenant.id)

        ged_url, tenant_ged_token = validate_tenant_plan_ged(tenant)

        mc = MayanClient(ged_url, tenant_ged_token)
        response = mc.document_simple_read(document.ged_id)

        if response.status_code == 404:
            message = "O documento não foi encontrado no GED. Possivelmente ele foi excluído diretamente no GED sem utilização do app Educa Legal. Verifique a lixeira no GED."
            logger.info(message)
            raise NotFound(message)

        response = mc.document_download(document.ged_id)
        f = io.BytesIO(response.content)

        return FileResponse(f, as_attachment=True, filename=document.name)

    def delete(self, request, identifier):

        """
        Exclui o documento do Educa Legal e do GED.

        Download requer como parâmetro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        204 Sucesso

        400 BAD REQUEST: Se o campo doc_uuid não for válido:
            => "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        403 FORBIDDEN: O cliente deve possuir GED para poder baixar documentos
            => "Somente clientes cadastrados num plano que possui GED podem baixar documentos."

        404 NOT FOUND: Se o documento (doc_uuid) não existir ou se o documento requisitado não pertencer ao cliente
            (tenant) ao qual o usuário da requisição está vinculado.

        404 NOT FOUND: Se o documento existir no Educa Legal mas não for encontrado no GED. Pode ocorrer de um usuário excluir o documento diretamente no GED.
            => "O documento não foi encontrado no GED. Possivelmente ele foi excluído diretamente no GED sem utilização do app Educa Legal.  Verifique a lixeira no GED."

        500 INTERNAL SERVER ERROR: Se o cliente estiver num plano que possui GED mas não há GED configurado para ele.
            => "O cliente está cadastrado num plano que possui GED mas mão há GED configurado para ele."

        500 INTERNAL SERVER ERROR: Se há GED cadastrado para o cliente mas não há URL ou TOKEN cadastrados.
            => "O GED do cliente não possui uma URL válida ou não possui token configurado"

        500 INTERNAL SERVER ERROR: Se houver problemas na conexão com o GED (não está disponível, por exemplo).
            => "Failed to establish a new connection: [Errno 111] Connection refused"


        :param request: HttpRequest
        :param identifier: id ou doc_uui do documento no Educa Legal
        :return: O arquivo do documento no GED
        """

        tenant = request.user.tenant

        if not checkers.is_uuid(identifier):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        elif checkers.is_uuid(identifier):
            document = get_object_or_404(self.queryset, doc_uuid=identifier, tenant=tenant.id)

        ged_url, tenant_ged_token = validate_tenant_plan_ged(tenant)

        mc = MayanClient(ged_url, tenant_ged_token)

        try:
            response = mc.document_delete(document.ged_id)
        except Exception as e:
            message = "Houve algum erro de comunicação ou de processamento com o GED: {e}".format(e=e)
            logger.info(message)
            raise APIException(message)

        if response.status_code == 404:
            message = "O documento não foi encontrado no GED. Possivelmente ele foi excluído diretamente no GED sem utilização do app Educa Legal. Verifique a lixeira no GED."
            logger.info(message)
            raise NotFound(message)
        elif response.status_code != 204:
            message = "Não foi possível excluir o documento do GED: {status_code} | {response}".format(status_code=response.status_code, response=response.json())
            logger.info(message)
            raise APIException(message)
        else:
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


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