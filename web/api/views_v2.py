import io
import logging
import pandas as pd

from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import viewsets, status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotFound,
    APIException,
)
from validator_collection import checkers

from api.third_party.mayan_client import MayanClient
from document.models import Document, DocumentFileKind, DocumentType
from document.views import save_document_data
from util.util import save_file_from_url
from document.views import validate_data_mongo, generate_document_from_mongo
from interview.models import Interview
from school.models import School, SchoolUnit
from tenant.models import Plan, Tenant, TenantGedData
from util.file_import import is_metadata_valid, is_content_valid
from util.mongo_util import create_dynamic_document_class

from .serializers_v2 import (
    PlanSerializer,
    DocumentSerializer,
    InterviewSerializer,
    SchoolSerializer,
    SchoolUnitSerializer,
    TenantSerializer,
)

logger = logging.getLogger(__name__)

UUID = "([a-z]|[0-9]){8}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){12}"


class TenantAwareAPIMixin:
    """
    Todas os ViewSets que restringem seu retorno às entidades pertencentes a um tenant apenas devem ser compostos
    por este mixim. Ele filtra o queryset a partir do Tenant do Usuário que faz a requisição. O usuário da requisição
    é o dono to token nela usado.
    """

    def get_queryset(self):
        tenant = self.request.user.tenant
        return self.queryset.filter(tenant=tenant)


# Administrative Views - Not filtered by Tenant - Requires Administrative Rigthes (is_staff = True )####################

class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a lista de todas as entrevistas ou os detalhes de uma entrevista.

    Disponível apenas para administradores.
    """

    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAdminUser]


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna dados dos planos disponíveis para contratação.

    Disponível apenas para administradores.
    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUser]


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a listagem de clientes (tenants) ou o cliente específico.

    Disponível apenas para administradores.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAdminUser]


# Document Views #######################################################################################################
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
            instance = get_object_or_404(
                self.queryset, doc_uuid=identifier, tenant=tenant_id
            )
        else:
            message = "O doc_uuid ou o id do documento não é um valor válido."
            logger.info(message)
            raise ValidationError(message)

        serializer = self.serializer_class(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lista todos os documentos principais do cliente (tenant).

        Somente documentos que pertencem ao cliente ao qual o usuário está associado são listados.

        200 Sucesso
        """
        tenant_id = request.user.tenant.id
        queryset = self.queryset.filter(tenant_id=tenant_id, parent=None)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Cria um novo documento

        Não é necessário informar o tenant no corpo da requisição. O sistema usa o cliente do usuário ao qual o usuário está vinculado.

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
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Atualiza parcialmente um documento já existente.

        Atualização requer como parâmetro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Tentativa de alteração de documento que não pertence ao cliente (tenant) ao qual o usuário está vinculado
            => "Não é permitido alterar o cliente (tenant) proprietário do documento."

        400 BAD REQUEST: Se o campo doc_uuid não for válido
            => "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        404 NOT FOUND: Se o documento (doc_uuid) não existir ou se o documento requisitado não pertencer ao cliente
        (tenant) ao qual o usuário da requisição está vinculado.
        """
        doc_uuid = kwargs["identifier"]
        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        else:
            tenant_id = request.user.tenant.id
            instance = get_object_or_404(
                self.queryset, doc_uuid=doc_uuid, tenant=tenant_id
            )

            if "tenant" in request.data:
                if tenant_id != int(request.data["tenant"]):
                    message = "Não é permitido alterar o cliente (tenant) proprietário do documento."
                    logger.info(message)
                    raise ValidationError(message)

            logger.info(
                "Atualizando o documento {doc_uuid}".format(doc_uuid=str(doc_uuid))
            )
            serializer = self.serializer_class(
                instance, data=request.data, partial=True, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # se o parametro 'trigger' = docassemble indica que o patch veio do docassemble
            params = self.request.query_params
            if 'trigger' in params:
                if params['trigger'] == 'docassemble':
                    data = self.request.data.copy()

                    # salva o documento no sistema de arquivos e/ou ged
                    save_document_file(instance, data, params)

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

        405 Método "DELETE" não é permitido: Se não for informado o doc_uuid
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
                instance = get_object_or_404(
                    self.queryset, doc_uuid=doc_uuid, tenant=tenant_id
                )
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


def save_in_ged(data, absolute_path, tenant):
    """Salva o arquivo no GED"""

    # se o cliente nao tem ged, nao envia para o ged
    mc = MayanClient(tenant.tenantgeddata.url, tenant.tenantgeddata.token)

    # salva o pdf no ged
    try:
        status_code, response, ged_id = mc.document_create(data, absolute_path)
    except Exception as e:
        message = 'Não foi possível inserir o pdf no GED. Erro: ' + str(e)
        logging.exception(message)

        return 0, message, 0
    else:
        if status_code != 201:
            message = 'Não foi possível inserir o pdf no GED. Erro: ' + str(status_code) + ' - ' + response
            logging.exception(message)

            return status_code, response, 0
        else:
            try:
                ged_document_data = mc.document_read(ged_id)
            except Exception as e:
                message = 'Não foi possível localizar o arquivo no GED. Erro: ' + str(e)
                logging.exception(message)
                return 0, message, 0

            return status_code, ged_document_data, ged_id


class DocumentDownloadViewSet(viewsets.ModelViewSet):

    queryset = Document.objects.all()
    # Este parametro é obrigatório em um ModelViewSet, embora não seja usado no presente exemplo
    serializer_class = DocumentSerializer

    def retrieve(self, request, *args, **kwargs):

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
        doc_uuid = kwargs["identifier"]
        tenant = request.user.tenant

        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        elif checkers.is_uuid(doc_uuid):
            document = get_object_or_404(
                self.queryset, doc_uuid=doc_uuid, tenant=tenant.id
            )

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

    def destroy(self, request, *args, **kwargs):

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

        doc_uuid = kwargs["identifier"]
        tenant = request.user.tenant

        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid não é um uuid válido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        elif checkers.is_uuid(doc_uuid):
            document = get_object_or_404(
                self.queryset, doc_uuid=doc_uuid, tenant=tenant.id
            )

        ged_url, tenant_ged_token = validate_tenant_plan_ged(tenant)

        mc = MayanClient(ged_url, tenant_ged_token)

        try:
            response = mc.document_delete(document.ged_id)
        except Exception as e:
            message = "Houve algum erro de comunicação ou de processamento com o GED: {e}".format(
                e=e
            )
            logger.info(message)
            raise APIException(message)

        if response.status_code == 404:
            message = "O documento não foi encontrado no GED. Possivelmente ele foi excluído diretamente no GED sem utilização do app Educa Legal. Verifique a lixeira no GED."
            logger.info(message)
            raise NotFound(message)
        elif response.status_code != 204:
            message = "Não foi possível excluir o documento do GED: {status_code} | {response}".format(
                status_code=response.status_code, response=response.json()
            )
            logger.info(message)
            raise APIException(message)
        else:
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


# Clients should authenticate by passing the token key in the "Authorization"
# HTTP header, prepended with the string "Token ".  For example:
# Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def validate_document(request, **kwargs):
    """
    Validate document received in request.body.

    * Requires token authentication.
    """

    # Transforma o dicionario em um dataframe
    data = pd.DataFrame.from_dict(request.data)

    try:
        # Valida os metadados do recebidos (tipos de campos e flags booleanas)
        # Se os dados forem validos, retorna dois dicionarios: o de tipos de campos e
        # os de obrigatoriedade dos registros
        # Ambos são usados para criar a classe dinamica
        (
            field_types_dict,
            required_fields_dict,
            metadata_valid,
        ) = is_metadata_valid(data)

    except ValueError as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)

        return Response({
            "status_code": 422,
            "error": message})

    # Valida o conteudo dos campos de acordo com seus tipos de dados e sua obrigadoriedade
    # trata os registros para valores aceitáveis pelos documentos
    # usando validators collection
    # Também valida se existe a coluna selected_school e school_division
    # Para outras validações de conteúdo, veja a função
    # Os campos vazios são transformados em None e deve ser tratados posteriormente ao fazer a chamada de API
    # do Docassemble para que não saiam como None ou com erro nos documentos
    # O campo school_division é transformado em ---
    try:
        (
            data_content,
            parent_fields_dict,
            error_messages,
            content_valid,
        ) = is_content_valid(data)
    except ValueError as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)

        return Response({
            "status_code": 422,
            "error": message})

    if not content_valid:
        return Response({
            "status_code": 422,
            "error": error_messages})

    # Se houver registro invalido, esta variavel sera definida como False ao final da funcao.
    # Esta variavel ira modifica a logica de exibicao das telas ao usuario:
    # Se o CSV for valido, i.e., tiver todos os registros validos, sera exibida a tela de envio
    # Se nao, exibe as mesnagens de sucesso e de erro na tela de carregar novamente o CSV
    data_valid = metadata_valid and content_valid

    try:
        interview = Interview.objects.get(pk=kwargs["interview_id"])
    except Interview.DoesNotExist:
        return Response({
            "status_code": 404,
            "error": "Não existe um tipo de documento com ID = {interview_id}".format(
                interview_id=kwargs["interview_id"]
            )})

    # verifica se informou um tipo de documento valido
    if interview.document_type.id not in DocumentType.id_choices():
        return Response({
            "status_code": 422,
            "error": "Os tipos de documento que permitem geração via API são {}".format(
                DocumentType.choices()
            )})

    try:
        # valida os dados recebidos de forma automatica no mongo
        mongo_document, dynamic_document_class_name, school_names_set, school_units_names_set = validate_data_mongo(
            request, interview.pk, data_valid, data_content, field_types_dict, required_fields_dict, parent_fields_dict,
            False)
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)

        return Response({
            "status_code": 400,
            "error": message})

    response_data = {"interview_id": interview.pk, "data_valid": data_valid}

    if not data_valid:
        mongo_document.drop_collection()

    return Response({
        "status_code": 200,
        "response_data": response_data,
        "dynamic_document_class_name": dynamic_document_class_name,
        "field_types_dict": field_types_dict,
        "required_fields_dict": required_fields_dict,
        "parent_fields_dict": parent_fields_dict,
        "school_names_set": school_names_set,
        "school_units_names_set": school_units_names_set
    })


# Clients should authenticate by passing the token key in the "Authorization"
# HTTP header, prepended with the string "Token ".  For example:
# Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def generate_document(request, **kwargs):
    """
    Validate and generate document received in request.body.

    * Requires token authentication.
    """
    try:
        # deve ser passado um request do django e não do drf
        response = validate_document(request._request, **kwargs)
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)
        return Response(message)

    # retorna erro caso os dados nao tenham sido validados
    if response.data['status_code'] != 200:
        return Response(response)

    dynamic_document_class = create_dynamic_document_class(
        response.data['dynamic_document_class_name'],
        response.data['field_types_dict'],
        response.data['required_fields_dict'],
        response.data['parent_fields_dict'],
        school_names_set=list(response.data['school_names_set']),
        school_units_names_set=list(response.data['school_units_names_set']),
    )

    try:
        success, data = generate_document_from_mongo(
            request._request, dynamic_document_class, kwargs["interview_id"])

        if success:
            return Response({
                "status_code": 200,
                "response_data": 'Documento gerado com sucesso'
            })
        else:
            return Response({
                "status_code": 400,
                "error": data
            })
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)

        return Response({
            "status_code": 400,
            "error": message})


def save_document_file(document, data, params):
    has_ged = document.tenant.has_ged()

    # salva o pdf no sistema de arquivos
    data['name'] = params['pdf_filename']
    relative_path = 'docassemble/' + params['pdf_filename'][:15]
    absolute_path, relative_file_path = save_file_from_url(params['pdf_url'], relative_path, params['pdf_filename'])
    document.file_kind = DocumentFileKind.PDF.value

    if has_ged:
        try:
            status_code, ged_data, ged_id = save_in_ged(data, absolute_path, document.tenant)
        except Exception as e:
            message = str(e)
            logging.exception(message)
        else:
            if status_code == 201:
                save_document_data(document, has_ged, ged_data, relative_file_path, None)
            else:
                message = 'Não foi possível salvar o documento no GED. {} - {}'.format(
                    str(status_code), ged_data)
                logging.error(message)
    else:
        save_document_data(document, has_ged, None, relative_file_path, None)

    # salva o docx no sistema de arquivos
    data['name'] = params['docx_filename']
    relative_path = 'docassemble/' + params['docx_filename'][:15]
    absolute_path, relative_file_path = save_file_from_url(params['docx_url'], relative_path, params['docx_filename'])

    # salva o docx como documento relacionado. copia do pai algumas propriedades
    related_document = Document(
        name=params['docx_filename'],
        description=document.description,
        interview=document.interview,
        school=document.school,
        tenant=document.tenant,
        bulk_generation=document.bulk_generation,
        file_kind=DocumentFileKind.DOCX.value,
    )

    if has_ged:
        try:
            status_code, ged_data, ged_id = save_in_ged(data, absolute_path, document.tenant)
        except Exception as e:
            message = str(e)
            logging.exception(message)
        else:
            if status_code == 201:
                save_document_data(related_document, has_ged, ged_data, relative_file_path, document)
            else:
                message = 'Não foi possível salvar o documento no GED. {} - {}'.format(
                    str(status_code), ged_data)
                logging.error(message)
    else:
        save_document_data(related_document, has_ged, None, relative_file_path, document)


# Front end views views - All filtered by tenant - They all follow the convention with TenantMODELViewSet
# and are composed by TenantAwareAPIMixin, which filters the queryset by tenant

class TenantSchoolViewSet(TenantAwareAPIMixin, viewsets.ModelViewSet):

    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class TenantSchoolUnitViewSet(viewsets.ModelViewSet):
    """
    Permite criar, alterar, listar e apagar as unidades das escolas.
    Só permite excluir escola vinculada ao tenant referente ao token informado.
    """
    queryset = SchoolUnit.objects.all()
    serializer_class = SchoolUnitSerializer

    def get_queryset(self):
        school_pk = self.kwargs["spk"]
        tenant = self.request.user.tenant
        queryset = self.queryset.filter(school_id=school_pk, tenant=tenant)
        return queryset


class TenantInterviewViewSet(TenantAwareAPIMixin, viewsets.ModelViewSet):

    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer


class TenantPlanViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_queryset(self):
        tenant = self.request.user.tenant
        return self.queryset.get(pk=tenant.plan_id)
