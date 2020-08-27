import logging
import io
from datetime import datetime
from datetime import timedelta
import pytz

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets
from rest_framework.exceptions import (
    ValidationError,
    PermissionDenied,
    NotFound,
    APIException,
)
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import api_view, renderer_classes
from validator_collection import checkers

from document.models import *
from interview.models import *
from school.models import *
from tenant.models import *
from users.models import CustomUser
from .mayan_helpers import MayanClient

from .serializers_v2 import (
    PlanSerializer,
    DocumentSerializer,
    DocumentDetailSerializer,
    DocumentCountSerializer,
    InterviewSerializer,
    SchoolSerializer,
    SchoolUnitSerializer,
    TenantSerializer,
    UserSerializer
)

logger = logging.getLogger(__name__)

UUID = "([a-z]|[0-9]){8}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){4}-([a-z]|[0-9]){12}"


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna a lista de todas as entrevistas ou os detalhes de uma entrevista.

    """
    serializer_class = InterviewSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            tenant = self.request.user.tenant
            queryset = tenant.interview_set.all()
        else:
            queryset = Interview.objects.all()
        queryset = queryset.order_by("name")
        return queryset


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retorna dados dos planos disponíveis para contratação.

    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            tenant = self.request.user.tenant
            queryset = self.queryset.filter(pk=tenant.plan_id)
            return queryset
        else:
            return self.queryset




class TenantViewSet(viewsets.ModelViewSet):
    """
    # Retorna a listagem de clientes (tenants) ou o cliente específico.
    #
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def create(self, request, *args, **kwargs):
        full_name = request.data.get("full_name").strip()
        tenant_name = request.data.get("tenant_name").strip()
        phone = request.data.get("phone").strip()
        email = request.data.get("email").strip()
        password = request.data.get("password")

        tenant = Tenant.objects.filter(name=tenant_name)
        if tenant:
            logger.info("Houve tentativa de criação de um tenant repetido pela auto-inscrição: " + tenant[0].name)
            return Response(
                "Já existe uma escola com esse nome. Favor escolher um nome diferente ou pedir à sua escola que o cadastre como usuário.",
                status=status.HTTP_200_OK)
        user = CustomUser.objects.filter(email=email)
        if user:
            logger.info("Houve tentativa de criação de um usuário repetido pela auto-inscrição: " + user[0].email)
            return Response(
                "Já existe uma usuário cadastrado com esse e-mail. Favor verificar se sua escola já está cadastrada no sistema ou usar outro e-mail.",
                status=status.HTTP_200_OK)
        logger.info("Novo tenant sendo criado:" + tenant_name)

        essential_plan = Plan.objects.get(pk=1)

        tenant = Tenant.objects.create(
            name=tenant_name,
            subdomain_prefix=None,
            eua_agreement=True,
            plan=essential_plan,
            auto_enrolled=True,
            esignature_app=None,
            phone=phone,
        )
        tenant.save()
        # Selects every freemium interview and adds to newly created tenant
        freemium_interviews = Interview.objects.filter(is_freemium=True)
        # https://docs.djangoproject.com/en/3.0/ref/models/relations/#django.db.models.fields.related.RelatedManager.add
        # add não aceita uma lista, mas um número arbitrário de objetos. Para expandir uma lista em vários objetos,
        # usamos *freemium_interviews antes da lista
        tenant.interview_set.add(*freemium_interviews)
        # splits the e-mail and uses the name part as username
        unsername = email.split('@')[0]
        # Splits the full name field into first and "rest of the name" for the user
        first_name = full_name.split()[0]
        last_name = ""
        for name in full_name.split()[1:]:
            last_name += " " + name
        last_name = last_name
        # Creates the user
        user = CustomUser.objects.create_user(username=unsername,
                                              first_name=first_name,
                                              last_name=last_name,
                                              email=email,
                                              password=password,
                                              tenant=tenant)
        user.save()
        return Response(status=status.HTTP_201_CREATED)


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

        serializer = DocumentDetailSerializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Lista todos os documentos do cliente (tenant).

        Somente documentos que pertencem ao cliente ao qual o usuário está associado são listados.

        200 Sucesso
        """
        paginator = LimitOffsetPagination()
        paginator.page_size = settings.REST_FRAMEWORK["PAGE_SIZE"]
        tenant_id = request.user.tenant.id
        queryset = self.queryset.filter(tenant_id=tenant_id)
        status_filter_param = request.query_params.getlist("status[]")
        school_filter_param = request.query_params.getlist("school[]")
        interview_filter_param = request.query_params.getlist("interview[]")
        order_by_created_date = request.query_params.get("orderByCreatedDate")
        created_date_range = request.query_params.get("createdDateRange")
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
            # O intevalo de datas vem como "01/08/2020" ou "01/08/2020 até 08/08/2020"
            # Abaixo o retorno é splitado no até (se houver) e cada data tem os espaços em branco nos extremos removidos
            dates_list = list(map(str.strip, created_date_range.split("até")))
            tz = pytz.timezone("America/Sao_Paulo")
            from_date = datetime.datetime.strptime(dates_list[0], '%d/%m/%Y')
            from_date = tz.localize(from_date)
            # Filtering a DateTimeFieldwith dates won’t include items on the last day, because the bounds are
            # interpreted as " 0am on the given date”. Por isso, somamos mais um ao dia para incluir o dia de fim
            if len(dates_list) == 1:
                to_date = from_date + timedelta(days=1)
                queryset = queryset.filter(created_date__range=(from_date, to_date))
            if len(dates_list) > 1:
                to_date = datetime.datetime.strptime(dates_list[1], '%d/%m/%Y')
                to_date += timedelta(days=1)
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


class DocumentCountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DocumentCount.objects.all()
    serializer_class = DocumentCountSerializer

    def get_queryset(self):
        tenant = self.request.user.tenant
        return self.queryset.get(pk=tenant.id)


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            tenant = self.request.user.tenant
            queryset = self.queryset.filter(tenant=tenant)
            return queryset
        else:
            return self.queryset


class SchoolUnitViewSet(viewsets.ModelViewSet):
    """
    Permite criar, alterar, listar e apagar as unidades das escolas.
    Só permite excluir escola vinculada ao tenant referente ao token informado.
    """
    queryset = SchoolUnit.objects.all()
    serializer_class = SchoolUnitSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            # https://github.com/axnsan12/drf-yasg/issues/333
            return SchoolUnit.objects.none()
        school_pk = self.kwargs["spk"]
        tenant = self.request.user.tenant
        queryset = self.queryset.filter(school_id=school_pk, tenant=tenant)
        return queryset


#################################### OTHERS ############################################################################

class UserView(APIView):
    def get(self, request):
        """
        Return a list of all users.
        """
        user = request.user
        user_data = UserSerializer(user)
        return Response(user_data.data)
