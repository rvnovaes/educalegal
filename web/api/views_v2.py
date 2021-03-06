import datetime
import io
import json
import logging
import pandas as pd
import pytz
import re

from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str, url_str_to_user_pk
from dateutil.relativedelta import relativedelta
from drf_yasg.renderers import SwaggerUIRenderer, OpenAPIRenderer
from json import dumps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework import pagination
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotFound,
    APIException,
)
from validator_collection import checkers

from django.core.files.storage import default_storage
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from api.third_party.mayan_client import MayanClient
from document.models import Document, DocumentFileKind, BulkDocumentKind
from document.util import send_email as doc_send_email, send_to_esignature as doc_send_to_esignature
from document.views import validate_data_mongo, generate_document_from_mongo, save_document_data, \
    reached_document_limit as doc_reached_document_limit
from interview.models import Interview, InterviewDocumentType
from school.models import School, SchoolUnit, Signatory, Grade
from tenant.models import Plan, Tenant, TenantGedData, ESignatureApp, ESignatureAppProvider
from users.models import CustomUser
from util.file_import import is_metadata_valid, is_content_valid
from util.mongo_util import create_dynamic_document_class
from util.util import delete_keys_from_obj

from .serializers_v2 import (
    PlanSerializer,
    DocumentSerializer,
    DocumentDetailSerializer,
    DocumentTypesSerializer,
    GradeSerializer,
    InterviewSerializer,
    SchoolSerializer,
    SchoolUnitSerializer,
    SignatorySerializer,
    TenantSerializer,
    TenantGedDataSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)

logger = logging.getLogger(__name__)

UUID = "([a-z]|[0-9]){8}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){12}"


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a lista de todas as entrevistas ou os detalhes de uma entrevista.

    """

    serializer_class = InterviewSerializer
    # Como o page size padrao esta definido no base.py como 50, precisamos sobrescrever esse default aqui
    # https://stackoverflow.com/questions/35432985/django-rest-framework-override-page-size-in-viewset
    pagination.PageNumberPagination.page_size = 150

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return Interview.objects.none()

        user = self.request.user
        if not user.is_superuser:
            tenant = self.request.user.tenant
            queryset = tenant.interview_set.all()
        else:
            queryset = Interview.objects.all()
        queryset = queryset.order_by("name")
        return queryset


class DocumentTypesViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = InterviewDocumentType.objects.all()
        queryset = queryset.order_by("name")
        serializer = DocumentTypesSerializer(queryset, many=True)
        return Response(serializer.data)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna dados dos planos dispon??veis para contrata????o.

    """

    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return Plan.objects.none()
        user = self.request.user
        if not user.is_superuser:
            tenant = self.request.user.tenant
            queryset = self.queryset.filter(pk=tenant.plan_id)
            return queryset
        else:
            return self.queryset


class TenantViewSet(viewsets.ModelViewSet):
    """
    # Retorna a listagem de clientes (tenants) ou o cliente espec??fico.
    # Inclui os dados do provedor de assinatura eletr??nica e do plano contratado.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def create_tenant(request):
    full_name = request.data.get("full_name").strip()
    tenant_name = request.data.get("tenant_name").strip()
    phone = request.data.get("phone").strip()
    email = request.data.get("email").strip()
    password = request.data.get("password")

    tenant = Tenant.objects.filter(name=tenant_name)
    if tenant:
        logger.info(
            "Houve tentativa de cria????o de um tenant repetido pela auto-inscri????o: "
            + tenant[0].name
        )
        return Response(
            "J?? existe uma inst??ncia com esse nome. Favor escolher um nome diferente ou pedir ?? sua escola que o cadastre como usu??rio.",
            status=status.HTTP_200_OK,
        )
    user = CustomUser.objects.filter(email=email)
    if user:
        logger.info(
            "Houve tentativa de cria????o de um usu??rio repetido pela auto-inscri????o: "
            + user[0].email
        )
        return Response(
            "J?? existe uma usu??rio cadastrado com esse e-mail. Favor verificar se sua escola j?? est?? cadastrada no sistema ou usar outro e-mail.",
            status=status.HTTP_200_OK,
        )
    logger.info("Novo tenant sendo criado:" + tenant_name)

    essential_plan = Plan.objects.get(pk=1)
    esignature_app = ESignatureApp.objects.filter(
        provider=ESignatureAppProvider.CLICKSIGN.name,
        test_mode=True).first()

    tenant = Tenant.objects.create(
        name=tenant_name,
        subdomain_prefix=None,
        eua_agreement=True,
        plan=essential_plan,
        auto_enrolled=True,
        esignature_app=esignature_app,
        phone=phone,
    )
    tenant.save()
    # Selects every freemium interview and adds to newly created tenant
    freemium_interviews = Interview.objects.filter(is_freemium=True)
    # https://docs.djangoproject.com/en/3.0/ref/models/relations/#django.db.models.fields.related.RelatedManager.add
    # add n??o aceita uma lista, mas um n??mero arbitr??rio de objetos. Para expandir uma lista em v??rios objetos,
    # usamos *freemium_interviews antes da lista
    tenant.interview_set.add(*freemium_interviews)
    # splits the e-mail and uses the name part as username
    username = email
    # Splits the full name field into first and "rest of the name" for the user
    first_name = full_name.split()[0]
    last_name = ""
    for name in full_name.split()[1:]:
        last_name += " " + name
    last_name = last_name
    # Creates the user
    user = CustomUser.objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        tenant=tenant,
    )
    user.save()

    # Creates the token for the user to create documents
    token = Token()
    token.user = user
    token.save()

    return Response(status=status.HTTP_201_CREATED)


# Document Views #######################################################################################################
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer

    def get_queryset(self):
        user = self.request.user
        document = Document.objects.annotate(document_data_as_text=Cast('document_data', TextField()))
        if not user.is_superuser:
            tenant = self.request.user.tenant
            return document.filter(tenant=tenant)
        else:
            return document.all()

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera o documento com base em um identificador (identifier).

        O identificador, neste m??todo, pode ser uma id (inteiro) ou doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        Somente documentos que pertencem ao cliente (tenant) ao qual o usu??rio est?? vinculado s??o recuperados.

        400 BAD REQUEST: Se for feita uma requisi????o e o valor informado n??o for um id num??rico (inteiro) ou n??o for um uuid v??lido, mno formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            => "O doc_uuid ou o id do documento n??o s??o valores v??lidos."

        404 NOT FOUND: Se o documento (id ou doc_uuid) n??o existir ou se o documento requisitado n??o pertencer ao cliente
        (tenant) ao qual o usu??rio da requisi????o est?? vinculado.

        500 INTERNAL SERVER ERROR: Se for retornado mais de um documento com o mesmo uuid.
            => "Mais de um documento foi recuperado com o mesmo uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        500 INTERNAL SERVER ERROR: Erro inespec??fico.
            "Ocorreu uma exce????o ao recuperar o documento (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"
        """
        try:
            tenant_id = request.user.tenant.id
            identifier = kwargs["identifier"]
            # Pode ser passada a id ou o doc_uuid.
            if checkers.is_integer(identifier, coerce_value=True):
                instance = get_object_or_404(self.get_queryset(), pk=identifier, tenant=tenant_id)
            elif checkers.is_uuid(identifier):
                instance = get_object_or_404(
                    self.get_queryset(), doc_uuid=identifier, tenant=tenant_id
                )
            else:
                message = "O doc_uuid ou o id do documento n??o ?? um valor v??lido."
                logger.info(message)
                raise ValidationError(message)

            serializer = DocumentDetailSerializer(instance)
            return Response(serializer.data)
        except MultipleObjectsReturned as e:
            error_message = "Mais de um documento foi recuperado com o mesmo uuid ({doc_uuid}): ".format(
                doc_uuid=identifier) + str(e)
            logger.error(error_message)
            return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            error_message = "Ocorreu uma exce????o ao recuperar o documento ({doc_uuid}): ".format(
                doc_uuid=identifier) + str(e)
            logger.error(error_message)
            return Response(error_message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        Lista todos os documentos principais do cliente (tenant).

        Somente documentos que pertencem ao cliente ao qual o usu??rio est?? associado s??o listados.

        200 Sucesso
        """
        paginator = LimitOffsetPagination()
        paginator.page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        document_name_filter_param = request.query_params.get("documentName")
        document_part_filter_param = request.query_params.get("documentPart")
        status_filter_param = request.query_params.getlist("status[]")
        school_filter_param = request.query_params.getlist("school[]")
        interview_filter_param = request.query_params.getlist("interview[]")
        order_by_created_date = request.query_params.get("orderByCreatedDate")
        created_date_range = request.query_params.get("createdDateRange")
        queryset = self.get_queryset().filter(parent=None).exclude(status="rascunho")
        if document_name_filter_param:
            queryset = queryset.filter(name__unaccent__icontains=document_name_filter_param)
        if document_part_filter_param:
            queryset = queryset.filter(document_data_as_text__unaccent__icontains=document_part_filter_param)
            # queryset = Document.objects.annotate(document_data_as_text=Cast('document_data', TextField())).filter(document_data_as_text__unaccent__icontains=document_part_filter_param)
        if status_filter_param:
            conditions = Q(status=status_filter_param[0])
            if len(status_filter_param) > 1:
                for s in status_filter_param[1:]:
                    conditions |= Q(status=s)
            queryset = queryset.filter(conditions)
        if school_filter_param:
            conditions = Q(school=school_filter_param[0])
            if len(school_filter_param) > 1:
                for id in school_filter_param[1:]:
                    conditions |= Q(school=id)
            queryset = queryset.filter(conditions)
        if interview_filter_param:
            conditions = Q(interview=interview_filter_param[0])
            if len(interview_filter_param) > 1:
                for id in interview_filter_param[1:]:
                    conditions |= Q(interview=id)
            queryset = queryset.filter(conditions)
        if created_date_range:
            # O intevalo de datas vem como "01/08/2020" ou "01/08/2020 at?? 08/08/2020"
            # Abaixo o retorno ?? splitado no at?? (se houver) e cada data tem os espa??os em branco nos extremos removidos
            dates_list = list(map(str.strip, created_date_range.split("at??")))
            tz = pytz.timezone("America/Sao_Paulo")
            from_date = datetime.datetime.strptime(dates_list[0], "%d/%m/%Y")
            from_date = tz.localize(from_date)
            # Filtering a DateTimeFieldwith dates won???t include items on the last day, because the bounds are
            # interpreted as " 0am on the given date???. Por isso, somamos mais um ao dia para incluir o dia de fim
            if len(dates_list) == 1:
                to_date = from_date + datetime.timedelta(days=1)
                queryset = queryset.filter(created_date__range=(from_date, to_date))
            if len(dates_list) > 1:
                to_date = datetime.datetime.strptime(dates_list[1], "%d/%m/%Y")
                to_date += datetime.timedelta(days=1)
                to_date = tz.localize(to_date)
                queryset = queryset.filter(created_date__range=(from_date, to_date))

        if order_by_created_date == "ascending":
            queryset.order_by("created_date")
        else:
            queryset.order_by("-created_date")

        page = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(page, many=True)
        # return Response(serializer.data)
        return paginator.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Cria um novo documento

        N??o ?? necess??rio informar o tenant no corpo da requisi????o. O sistema usa o cliente do usu??rio ao qual o usu??rio est?? vinculado.

        400 BAD REQUEST: Se for tentada a cria????o de um documento em um cliente (tenant) distinto daquele ao qual o usu??rio est?? vinculado.
            => "Somente ?? permitida a cria????o de documentos no seu cliente (tenant)."
        """
        tenant_id = request.user.tenant.id
        if "tenant" in request.data:
            if tenant_id != int(request.data["tenant"]):
                message = "Somente ?? permitida a cria????o de documentos no seu cliente (tenant)."
                logger.info(message)
                raise ValidationError(message)
        else:
            request.data["tenant"] = tenant_id

        status_code, message = self.verify_ged_settings()
        if status_code != status.HTTP_200_OK:
            return Response(message, status=status_code)
        else:
            return super(DocumentViewSet, self).create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Atualiza parcialmente um documento j?? existente.

        Atualiza????o requer como par??metro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Tentativa de altera????o de documento que n??o pertence ao cliente (tenant) ao qual o usu??rio est?? vinculado
            => "N??o ?? permitido alterar o cliente (tenant) propriet??rio do documento."

        400 BAD REQUEST: Se o campo doc_uuid n??o for v??lido
            => "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        404 NOT FOUND: Se o documento (doc_uuid) n??o existir ou se o documento requisitado n??o pertencer ao cliente
        (tenant) ao qual o usu??rio da requisi????o est?? vinculado.
        """
        doc_uuid = kwargs["identifier"]
        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        else:
            tenant_id = request.user.tenant.id
            instance = get_object_or_404(
                self.get_queryset(), doc_uuid=doc_uuid, tenant=tenant_id
            )

            if "tenant" in request.data:
                if tenant_id != int(request.data["tenant"]):
                    message = "N??o ?? permitido alterar o cliente (tenant) propriet??rio do documento."
                    logger.info(message)
                    raise ValidationError(message)

            logger.info(
                "Atualizando o documento {doc_uuid}".format(doc_uuid=str(doc_uuid))
            )

            # faz copia do request.data, pois nao ?? permitido alterar diretamente no request.data
            data = request.data.copy()

            # como vem do docassemble como uma string e n??o um json, tem que colocar colchetes na string
            # para torn??-la um JSON string v??lido e poder usar o json.loads()
            valid_json_string = "[" + data['document_data'] + "]"
            document_data = json.loads(valid_json_string)
            # pega somente o dicionario
            document_data = document_data[0]

            # limpa a variavel all_variables antes de salvar no sistema
            data['document_data'] = clean_all_variables(document_data)

            serializer = DocumentDetailSerializer(
                instance, data=data, partial=True, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # se o parametro 'trigger' = docassemble indica que o patch veio do docassemble
            params = self.request.query_params
            if 'trigger' in params:
                if params['trigger'] == 'docassemble':
                    # salva o documento no sistema de arquivos e/ou ged
                    status_code, message = save_document_file(instance, data, params)

                    if status_code != status.HTTP_200_OK:
                        Response.status_code = status_code
                        return Response({"status_code": status_code, "message": message})

            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Exclui o documento.

        Exclus??o requer como par??metro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Se o campo doc_uuid n??o for v??lido:
            => "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        403 FORBIDDEN: Tentativa de exlus??o de documento por usu??rio sem permiss??es (is_staff = True).
            => "Somente usu??rios administradores podem excluir documentos."

        404 NOT FOUND: Se o documento (doc_uuid) n??o existir ou se o documento requisitado n??o pertencer ao cliente
        (tenant) ao qual o usu??rio da requisi????o est?? vinculado.

        405 M??todo "DELETE" n??o ?? permitido: Se n??o for informado o doc_uuid
        """
        doc_uuid = kwargs["identifier"]
        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        else:
            user = request.user
            if user.is_staff:
                tenant_id = request.user.tenant.id
                instance = get_object_or_404(
                    self.get_queryset(), doc_uuid=doc_uuid, tenant=tenant_id
                )
                self.perform_destroy(instance)
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                message = "Somente usu??rios administradores podem excluir documentos."
                logger.info(message)
                raise PermissionDenied(message)

    def verify_ged_settings(self):
        try:
            tenant_id = self.request.data['tenant']
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            message = 'A inst??ncia com ID = {} n??o foi encontrado.'.format(tenant_id)
            return status.HTTP_404_NOT_FOUND, message
        except Exception as e:
            message = str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return status.HTTP_400_BAD_REQUEST, message
        else:
            if tenant.has_ged():
                mc = MayanClient(tenant.tenantgeddata.url, tenant.tenantgeddata.token)

                try:
                    interview_id = self.request.data['interview']
                    interview = Interview.objects.get(pk=interview_id)
                except Interview.DoesNotExist:
                    message = 'A entrevista com ID = {} n??o foi encontrada.'.format({interview_id})
                    return status.HTTP_404_NOT_FOUND, message
                except Exception as e:
                    message = str(type(e).__name__) + " : " + str(e)
                    logger.error(message)
                    return status.HTTP_400_BAD_REQUEST, message

                document_type_id = interview.document_type_id

                # verifica se existe no ged o tipo de documento da entrevista selecionada
                try:
                    document_type_data = mc.document_type_read(document_type_id)
                except Exception as e:
                    message = str(type(e).__name__) + " : " + str(e)
                    logger.error(message)
                    return status.HTTP_400_BAD_REQUEST, message
                else:
                    if 'detail' in document_type_data:
                        if document_type_data['detail'] == 'Invalid token.':
                            message = 'O token do usu??rio do GED est?? inv??lido ou n??o existe.'
                            return status.HTTP_404_NOT_FOUND, message

                        # json_encode($response, JSON_UNESCAPED_UNICODE);
                        if (document_type_data['detail'] == 'Not found.') or \
                                (document_type_data['detail'] == 'N\u00e3o encontrado.'):
                            message = 'N??o existe o tipo de documento com ID = {} cadastrado no GED.'.format(
                                document_type_id)

                            return status.HTTP_404_NOT_FOUND, message

        return status.HTTP_200_OK, 'Configura????o do GED OK'


def clean_all_variables(all_variables):
    keys_to_ignore = ['DocumentStatus', 'Enum', 'PY2', '__warningregistry__', '_class', '_internal', 'ask_number',
                      'ask_object_type', 'attachments', 'auto_gather', 'cd_name', 'cd_related_documents', 'cd_status',
                      'city_only', 'complete', 'complete_attribute', 'content_document', 'custom_file_name',
                      'device_local', 'doc_uuid', 'document_type_data', 'educalegal_front_url', 'educalegal_url',
                      'el_environment', 'el_log_to_console', 'el_send_email', 'elc', 'envelope_statuses',
                      'example_acordo_individual_reducao_de_jornada_e_reducao_salarial',
                      'example_termo_acordo_individual_para_banco_horas_mp_927_2020',
                      'example_termo_mudanca_de_regime_e_cessao_do_direito_autoral', 'gathered', 'generated_file',
                      'geolocated', 'help_email_msg', 'i', 'input_installments_list', 'installments_list',
                      'instanceName', 'interview_custom_file_name_string', 'interview_data', 'interview_document_type',
                      'interview_is_freemium', 'interview_language', 'intid', 'item', 'job_title_list', 'location',
                      'mc', 'menu_items', 'minimum_number', 'mongo_uuid', 'nav', 'new_recipient', 'object_type',
                      'object_type_parameters', 'plan_data', 'plan_use_esignature', 'plan_use_ged',
                      'recipient_group_types_dict', 'recipients', 'reviewed_school_email_answer', 'revisit',
                      'school_data_dict', 'school_id', 'school_letterhead', 'school_names_list', 'school_units',
                      'school_units_dict', 'school_units_list', 'school_signingperson_dict', 'session_local',
                      'signature_local_default', 'state_initials_list', 'string_types', 'table', 'target_number',
                      'tenant_data', 'tenant_esignature_data', 'tenant_ged_data', 'tenant_ged_token', 'tenant_ged_url',
                      'there_are_any', 'tid', 'url_args', 'user_local', 'uses_parts', 'ut', 'v', 'valid_data',
                      'signingperson_data_list', 'grades_list', 'grades_select', 'grades_default', 'witnesses_list',
                      'signatories_esw', 'signatories_list']

    # ignora valid_*_table: ex.: valid_employees_table, valid_locatarios_table
    regex_list = ['valid_(.*)_table']
    ignore = {k for k, v in all_variables.items() if any(re.match(regex, k) for regex in regex_list)}
    ignore = list(ignore)
    keys_to_ignore += ignore

    interview_variables = delete_keys_from_obj(all_variables, keys_to_ignore)

    # converte dicionario em json
    interview_variables = json.dumps(interview_variables)
    return interview_variables


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
            message = "O cliente est?? cadastrado num plano que possui GED mas m??o h?? GED configurado para ele."
            logger.info(message)
            raise APIException(message)

        # Aqui preferimos testar o tamanho da URL ao inv??s de fazer o checker.is_url, uma vez que, em ambiente de dev,
        # se usar, eg, http://ged:8000 a valida????o falha

        if not len(ged_url) or len(tenant_ged_token) == 0:
            message = "O GED do cliente n??o possui uma URL v??lida ou n??o possui token configurado"
            logger.info(message)
            raise APIException(message)

        return ged_url, tenant_ged_token


def save_in_ged(data, url, file, tenant):
    """Salva o arquivo no GED"""

    # se o cliente nao tem ged, nao envia para o ged
    mc = MayanClient(tenant.tenantgeddata.url, tenant.tenantgeddata.token)

    # salva o arquivo no ged
    try:
        status_code, response, ged_id = mc.document_create(data, url, file)
    except Exception as e:
        message = 'N??o foi poss??vel inserir o arquivo no GED. Erro: ' + str(e)
        logging.error(message)

        return 500, message, 0
    else:
        if isinstance(response, dict):
            response = dumps(response)

        if status_code != 201:
            message = 'N??o foi poss??vel inserir o arquivo no GED. Erro: ' + str(status_code) + ' - ' + str(response)
            logging.error(message)

            return status_code, response, 0
        else:
            if ged_id == 0:
                message = 'O arquivo foi inserido no GED, mas retornou ID = 0. Erro: ' + str(status_code) + ' - ' + \
                          str(response)
                logging.error(message)

                return status_code, message, 0
            else:
                try:
                    ged_document_data = mc.document_read(ged_id)
                except Exception as e:
                    message = 'N??o foi poss??vel localizar o arquivo no GED. Erro: ' + str(e)
                    logging.error(message)
                    return 500, message, 0

            return status_code, ged_document_data, ged_id


class DocumentDownloadViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    # Este parametro ?? obrigat??rio em um ModelViewSet, embora n??o seja usado no presente exemplo
    serializer_class = DocumentSerializer

    def retrieve(self, request, *args, **kwargs):

        """
        Baixa o documento do GED.

        Download requer como par??metro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Se o campo doc_uuid n??o for v??lido:
            => "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        403 FORBIDDEN: O cliente deve possuir GED para poder baixar documentos
            => "Somente clientes cadastrados num plano que possui GED podem baixar documentos."

        404 NOT FOUND: Se o documento (doc_uuid) n??o existir ou se o documento requisitado n??o pertencer ao cliente
            (tenant) ao qual o usu??rio da requisi????o est?? vinculado.

        404 NOT FOUND: Se o documento existir no Educa Legal mas n??o for encontrado no GED. Pode ocorrer de um usu??rio excluir o documento diretamente no GED.
            => "O documento n??o foi encontrado no GED. Possivelmente ele foi exclu??do diretamente no GED sem utiliza????o do app Educa Legal.  Verifique a lixeira no GED."

        500 INTERNAL SERVER ERROR: Se o cliente estiver num plano que possui GED mas n??o h?? GED configurado para ele.
            => "O cliente est?? cadastrado num plano que possui GED mas m??o h?? GED configurado para ele."

        500 INTERNAL SERVER ERROR: Se h?? GED cadastrado para o cliente mas n??o h?? URL ou TOKEN cadastrados.
            => "O GED do cliente n??o possui uma URL v??lida ou n??o possui token configurado"

        500 INTERNAL SERVER ERROR: Se houver problemas na conex??o com o GED (n??o est?? dispon??vel, por exemplo).
            => "Failed to establish a new connection: [Errno 111] Connection refused"


        :param request: HttpRequest
        :param identifier: id ou doc_uui do documento no Educa Legal
        :return: O arquivo do documento no GED
        """
        doc_uuid = kwargs["identifier"]
        tenant = request.user.tenant

        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
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
            message = "O documento n??o foi encontrado no GED. Possivelmente ele foi exclu??do diretamente no GED sem utiliza????o do app Educa Legal. Verifique a lixeira no GED."
            logger.info(message)
            raise NotFound(message)

        response = mc.document_download(document.ged_id)
        f = io.BytesIO(response.content)

        return FileResponse(f, as_attachment=True, filename=document.name)

    def destroy(self, request, *args, **kwargs):

        """
        Exclui o documento do Educa Legal e do GED.

        Download requer como par??metro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        204 Sucesso

        400 BAD REQUEST: Se o campo doc_uuid n??o for v??lido:
            => "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        403 FORBIDDEN: O cliente deve possuir GED para poder baixar documentos
            => "Somente clientes cadastrados num plano que possui GED podem baixar documentos."

        404 NOT FOUND: Se o documento (doc_uuid) n??o existir ou se o documento requisitado n??o pertencer ao cliente
            (tenant) ao qual o usu??rio da requisi????o est?? vinculado.

        404 NOT FOUND: Se o documento existir no Educa Legal mas n??o for encontrado no GED. Pode ocorrer de um usu??rio excluir o documento diretamente no GED.
            => "O documento n??o foi encontrado no GED. Possivelmente ele foi exclu??do diretamente no GED sem utiliza????o do app Educa Legal.  Verifique a lixeira no GED."

        500 INTERNAL SERVER ERROR: Se o cliente estiver num plano que possui GED mas n??o h?? GED configurado para ele.
            => "O cliente est?? cadastrado num plano que possui GED mas m??o h?? GED configurado para ele."

        500 INTERNAL SERVER ERROR: Se h?? GED cadastrado para o cliente mas n??o h?? URL ou TOKEN cadastrados.
            => "O GED do cliente n??o possui uma URL v??lida ou n??o possui token configurado"

        500 INTERNAL SERVER ERROR: Se houver problemas na conex??o com o GED (n??o est?? dispon??vel, por exemplo).
            => "Failed to establish a new connection: [Errno 111] Connection refused"


        :param request: HttpRequest
        :param identifier: id ou doc_uui do documento no Educa Legal
        :return: O arquivo from school.models import School, SchoolUnitdo documento no GED
        """

        doc_uuid = kwargs["identifier"]
        tenant = request.user.tenant

        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
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
            message = "Houve algum erro de comunica????o ou de processamento com o GED: {e}".format(
                e=e
            )
            logger.info(message)
            raise APIException(message)

        if response.status_code == 404:
            message = "O documento n??o foi encontrado no GED. Possivelmente ele foi exclu??do diretamente no GED sem utiliza????o do app Educa Legal. Verifique a lixeira no GED."
            logger.info(message)
            raise NotFound(message)
        elif response.status_code != 204:
            message = "N??o foi poss??vel excluir o documento do GED: {status_code} | {response}".format(
                status_code=response.status_code, response=response.json()
            )
            logger.info(message)
            raise APIException(message)
        else:
            document.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentCloudDownloadViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    # Este parametro ?? obrigat??rio em um ModelViewSet, embora n??o seja usado no presente exemplo
    serializer_class = DocumentSerializer

    def retrieve(self, request, *args, **kwargs):

        """
        Baixa o documento do GED.

        Download requer como par??metro doc_uuid (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

        400 BAD REQUEST: Se o campo doc_uuid n??o for v??lido:
            => "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

        404 NOT FOUND: Se o documento (doc_uuid) n??o existir ou se o documento requisitado n??o pertencer ao cliente
            (tenant) ao qual o usu??rio da requisi????o est?? vinculado.

        :param request: HttpRequest
        :return: O arquivo do documento no cloud
        """
        doc_uuid = kwargs["identifier"]
        tenant = request.user.tenant

        if not checkers.is_uuid(doc_uuid):
            message = "O doc_uuid n??o ?? um uuid v??lido. O uuid deve ter o formato: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            logger.info(message)
            raise ValidationError(message)
        elif checkers.is_uuid(doc_uuid):
            document = get_object_or_404(self.queryset, doc_uuid=doc_uuid, tenant=tenant.id)

        file = default_storage.open(document.cloud_file.name, 'rb')
        file_content = file.read()
        f = io.BytesIO(file_content)

        return FileResponse(f, as_attachment=True, filename=document.name)


# Clients should authenticate by passing the token key in the "Authorization"
# HTTP header, prepended with the string "Token ".  For example:
# Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
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
        # Ambos s??o usados para criar a classe dinamica
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
    # trata os registros para valores aceit??veis pelos documentos
    # usando validators collection
    # Tamb??m valida se existe a coluna selected_school e school_division
    # Para outras valida????es de conte??do, veja a fun????o
    # Os campos vazios s??o transformados em None e deve ser tratados posteriormente ao fazer a chamada de API
    # do Docassemble para que n??o saiam como None ou com erro nos documentos
    # O campo school_division ?? transformado em ---
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
            "error": "N??o existe entrevista com ID = {interview_id}".format(
                interview_id=kwargs["interview_id"]
            )})

    # verifica se informou um tipo de documento valido
    if interview.document_type.id not in BulkDocumentKind.id_choices():
        return Response({
            "status_code": 422,
            "error": "O tipo de documento informado ID = {id} n??o est?? na lista dos que permitem gera????o via API: "
                     "{document_types}".format(id=interview.document_type.id, document_types=BulkDocumentKind.choices())
        })

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
        "mongo_document_id": str(mongo_document.id),
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
@permission_classes([IsAuthenticated])
def generate_document(request, **kwargs):
    """
    Validate and generate document received in request.body.

    * Requires token authentication.
    """
    try:
        # deve ser passado um request do django e n??o do drf
        response = validate_document(request._request, **kwargs)
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)
        return Response(message)

    # retorna erro caso os dados nao tenham sido validados
    if response.status_code != 200:
        return Response(response)

    if 'status_code' in response.data:
        if response.data['status_code'] != 200:
            return Response(response.data)

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
            request._request, dynamic_document_class, kwargs["interview_id"], response.data['mongo_document_id'])

        if success:
            return Response({
                "status_code": 201,
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
    data['label'] = data['name']
    relative_path = 'docs/' + document.tenant.name + '/' + params['pdf_filename'][:15] + '/'

    document.file_kind = DocumentFileKind.PDF.value
    status_code = 400
    if has_ged:
        try:
            status_code, ged_data, ged_id = save_in_ged(data, params['pdf_url'], None, document.tenant)
        except Exception as e:
            message = str(e)
            logging.exception(message)
            return status_code, message
        else:
            if status_code == 201:
                if 'id' in ged_data['id']:
                    save_document_data(document, params['pdf_url'], None, relative_path, has_ged, ged_data,
                                       params['pdf_filename'], None)
                else:
                    message = 'N??o foi gerado o link do PDF do documento {} no GED. Entre em contato com o ' \
                              'suporte.'.format(document.doc_uuid)
                    logging.error(message)
                    return status.HTTP_400_BAD_REQUEST, message
            else:
                message = 'N??o foi poss??vel salvar o documento no GED. {} - {}'.format(
                    str(status_code), ged_data)
                logging.error(message)
                return status.HTTP_400_BAD_REQUEST, message
    else:
        save_document_data(document, params['pdf_url'], None, relative_path, has_ged, None, params['pdf_filename'],
                           None)

    # salva o docx no sistema de arquivos
    if 'docx_filename' in params:
        data['name'] = params['docx_filename']
        data['label'] = data['name']
        relative_path = 'docs/' + document.tenant.name + '/' + params['docx_filename'][:15] + '/'

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

        # limpa a variavel
        status_code = 0
        if has_ged:
            try:
                status_code, ged_data, ged_id = save_in_ged(data, params['docx_url'], None, document.tenant)
            except Exception as e:
                message = str(e)
                logging.exception(message)
                return status_code, message
            else:
                if status_code == 201:
                    if 'id' in ged_data['id']:
                        save_document_data(related_document, params['docx_url'], None, relative_path, has_ged, ged_data,
                                       params['docx_filename'], document)
                    else:
                        message = 'N??o foi gerado o link do DOCX do documento {} no GED. Entre em contato com o ' \
                                  'suporte.'.format(document.doc_uuid)
                        logging.error(message)
                        return status.HTTP_400_BAD_REQUEST, message
                else:
                    message = 'N??o foi poss??vel salvar o documento no GED. {} - {}'.format(
                        str(status_code), ged_data)
                    logging.error(message)
                    return status.HTTP_400_BAD_REQUEST, message
        else:
            save_document_data(related_document, params['docx_url'], None, relative_path, has_ged, None,
                               params['docx_filename'], document)

    return status.HTTP_200_OK, 'Feito o upload do documento'


# Front end views views - All filtered by tenant - They all follow the convention with TenantMODELViewSet
# and are composed by TenantAwareAPIMixin, which filters the queryset by tenant

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return School.objects.none()
        user = self.request.user
        if not user.is_superuser:
            tenant = self.request.user.tenant
            queryset = self.queryset.filter(tenant=tenant)
            return queryset
        else:
            return self.queryset

    def destroy(self, request, *args, **kwargs):
        school = School.objects.get(pk=kwargs.get("pk"))
        school_documents = Document.objects.filter(school=school)
        if school_documents:
            return Response(
                "N??o ?? poss??vel excluir esta escola porque ela possui documentos gerados.",
                status=status.HTTP_200_OK,
            )
        else:
            school.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class SchoolUnitViewSet(viewsets.ModelViewSet):
    """
    Permite criar, alterar, listar e apagar as unidades das escolas.
    S?? permite excluir escola vinculada ao tenant referente ao token informado.
    """

    queryset = SchoolUnit.objects.all()
    serializer_class = SchoolUnitSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return SchoolUnit.objects.none()
        school_pk = self.kwargs["spk"]
        tenant = self.request.user.tenant
        queryset = self.queryset.filter(school_id=school_pk, tenant=tenant)
        return queryset


class SignatoryViewSet(viewsets.ModelViewSet):
    """
    Permite criar, alterar, listar e apagar os tipos de signat??rios das escolas.
    S?? permite excluir os signat??rios vinculados ao tenant referente ao token informado.
    """

    queryset = Signatory.objects.all()
    serializer_class = SignatorySerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return Signatory.objects.none()
        school_pk = self.kwargs["spk"]
        tenant = self.request.user.tenant
        queryset = self.queryset.filter(school_id=school_pk, tenant=tenant)
        return queryset


class GradeViewSet(viewsets.ModelViewSet):
    """
    Permite criar, alterar, listar e apagar as s??ries escolares.
    S?? permite excluir os signat??rios vinculados ao tenant referente ao token informado.
    """

    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return Grade.objects.none()
        school_pk = self.kwargs["spk"]
        tenant = self.request.user.tenant
        queryset = self.queryset.filter(school_id=school_pk, tenant=tenant)
        return queryset


class TenantGedDataViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TenantGedData.objects.all()
    serializer_class = TenantGedDataSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-+/issues/333
            return TenantGedData.objects.none()
        user_tenant = self.request.user.tenant
        tenant = Tenant.objects.get(pk=self.kwargs.get("pk"))
        if user_tenant == tenant:
            return self.queryset
        else:
            message = "O usu??rio n??o tem autoriza????o para acessar estes dados."
            logger.info(message)
            raise PermissionDenied(message)


class UserView(APIView):
    def get(self, request):
        """
        Return a list of all users.
        """
        user = request.user
        user_data = UserSerializer(user)
        return Response(user_data.data)


@api_view(["GET"])
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def dashboard_data(request):
    tenant = request.user.tenant
    user = request.user
    if not user.is_superuser:
        total_docs = Document.objects.filter(tenant=tenant)
    else:
        total_docs = Document.objects.all()
    total_docs = total_docs.filter(parent=None)
    use_ged = tenant.plan.use_ged
    now = datetime.datetime.now()
    tz = pytz.timezone("America/Sao_Paulo")
    begin_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    begin_last_month = begin_of_month - relativedelta(months=1)
    tz.localize(begin_of_month)
    tz.localize(begin_last_month)
    total_docs_count = total_docs.count()
    # TODO excluir os documentos filhos
    # Current Month Documents
    cm_docs = total_docs.filter(created_date__gte=begin_of_month)
    # Last Month Documents
    lm_docs = total_docs.filter(created_date__gte=begin_last_month,
                                created_date__lt=begin_of_month)
    # Se usa GED, consideramos finalizado somente depois do envio para o GED. Portanto, excluimos da contagem
    # tamb??m os documentos criados
    if use_ged:
        cm_docs_count = cm_docs.exclude(Q(status="rascunho") | Q(status="criado")).count()
        lm_docs_count = lm_docs.exclude(Q(status="rascunho") | Q(status="criado")).count()
        cm_in_progress_docs_count = cm_docs.filter(Q(status="rascunho") | Q(status="criado")).count()
        lm_in_progress_docs_count = lm_docs.filter(Q(status="rascunho") | Q(status="criado")).count()
    else:
        cm_docs_count = cm_docs.exclude(status="rascunho").count()
        lm_docs_count = lm_docs.exclude(status="rascunho").count()
        cm_in_progress_docs_count = cm_docs.filter(status="rascunho").count()
        lm_in_progress_docs_count = lm_docs.filter(status="rascunho").count()

    cm_signature_count = cm_docs.filter(Q(status="assinado") | Q(status="assinatura recusada/inv??lida")).count()
    lm_signature_count = lm_docs.filter(Q(status="assinado") | Q(status="assinatura recusada/inv??lida")).count()
    cm_in_progress_signature_count = cm_docs.filter(status="enviado para assinatura").count()
    lm_in_progress_signature_count = lm_docs.filter(status="enviado para assinatura").count()

    return Response(
        {
            "tenant_name": tenant.name,
            "total_docs_count": total_docs_count,
            "cm_docs_count": cm_docs_count,
            "lm_docs_count": lm_docs_count,
            "cm_in_progress_docs_count": cm_in_progress_docs_count,
            "lm_in_progress_docs_count": lm_in_progress_docs_count,
            "cm_signature_count": cm_signature_count,
            "lm_signature_count": lm_signature_count,
            "cm_in_progress_signature_count": cm_in_progress_signature_count,
            "lm_in_progress_signature_count": lm_in_progress_signature_count,
        }
    )


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def recover_password(request):
    email = request.data.get("email")
    try:
        user = CustomUser.objects.get(email=email)
        # Adaptado de  allauth.account.forms.ResetPasswordForm.save()
        current_site = get_current_site(request)
        temp_key = default_token_generator.make_token(user)
        # Regista a temp key no usuario para conferencia posterior quando da redefinicao da senha. A temp_key e gravada
        # tamb??m com created_date = now, para verificar sua validade.
        user.temp_key = temp_key
        user.save()
        # send the password reset email
        path = "/redefinir/" + user_pk_to_url_str(user) + "-" + temp_key
        url = "https://" + current_site.domain + path
        context = {
            "current_site": current_site,
            "user": user,
            "password_reset_url": url,
            "request": request,
        }

        get_adapter(request).send_mail(
            "account/email/password_reset_key", email, context
        )

        log_message = "Houve tentativa de recupera????o de senha com e-mail {email}".format(
            email=email
        )
        logger.info(log_message)

    except CustomUser.DoesNotExist:
        log_message = "Houve tentativa de recupera????o de senha com e-mail inv??lido {email}".format(
            email=email
        )
        logger.info(log_message)

    message = "Se houver usu??rio associado a este e-mail, em breve voc?? receber?? instru????es para recupera????o da senha."
    return Response(message)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def reset_password(request):
    password = request.data.get("password")
    key = request.data.get("key")
    user_id_str = key.split("-")[0]
    user_id = url_str_to_user_pk(user_id_str)
    temp_key = key[len(user_id_str) + 1:]
    try:
        user = CustomUser.objects.get(pk=user_id)
        now = timezone.now()
        ten_minutes_ago = now - relativedelta(minutes=10)
        if user.temp_key:
            if (
                    user.temp_key != temp_key
                    or (user.temp_key_created_date - ten_minutes_ago).total_seconds() > 600
            ):
                message = "A chave de redefini????o est?? expirada. Favor refazer o processo de redefini????o de senha."
                return Response(message, status=status.HTTP_403_FORBIDDEN)
            else:
                user.set_password(password)
                user.temp_key = None
                user.temp_key_created_date = None
                user.save()
                message = "A senha foi alterada com sucesso!"
                return Response(message)
        else:
            log_message = "Foi feita uma tentativa de recupera????o de senha sem temp_key definida: {temp_key}".format(
                temp_key=temp_key
            )
            logger.error(log_message)
            return Response(log_message, status=status.HTTP_403_FORBIDDEN)
    except CustomUser.DoesNotExist:
        log_message = "Foi feita uma tentativa de recupera????o de senha com um usu??rio inexistente {temp_key}".format(
            temp_key=temp_key
        )
        logger.info(log_message)
        # Mesmo assim a mensagem ?? a mesma para evitar informar se o user existe ou n??o
        message = "A chave de redefini????o est?? expirada. Favor refazer o processo de redefini????o de senha."
        return Response(message, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_email(request):
    doc_uuid = request.data.get("doc_uuid")
    status_code, message = doc_send_email(doc_uuid)

    return Response(message, status=status_code)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_to_esignature(request):
    doc_uuid = request.data.get("doc_uuid")
    status_code, message = doc_send_to_esignature(doc_uuid)

    return Response(message, status=status_code)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reached_document_limit(request):
    try:
        reached_limit, document_limit = doc_reached_document_limit(request.user.tenant_id)
        message = {"reached_limit": reached_limit,
                   "document_limit": document_limit
                   }
        return Response(message, status=status.HTTP_200_OK)

    except Exception as e:
        message = 'N??o foi poss??vel obter o limite de documentos. Erro: {}'.format(e)
        return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangePassword(APIView):
    """
    An endpoint for changing password.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            new_password1 = serializer.data.get("new_password1")
            new_password2 = serializer.data.get("new_password2")
            if not self.object.check_password(old_password):
                message = "A senha atual est?? inv??lida."
                return Response(message, status=status.HTTP_400_BAD_REQUEST)

            if old_password:
                if old_password == new_password1:
                    message = "A nova senha deve ser diferente da atual."
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)

            if new_password1 and new_password2:
                if new_password1 != new_password2:
                    message = "A nova senha deve ser igual ?? sua confirma????o."
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password1"))
            self.object.force_password_change = False
            self.object.save()
            message = "A senha foi alterada com sucesso!"
            return Response(message, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
