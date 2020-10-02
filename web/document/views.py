import logging
import json
import pandas as pd
import uuid

from celery import chain
from datetime import datetime
from mongoengine.errors import ValidationError
from rest_framework import generics
from urllib.request import urlretrieve, urlcleanup

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django_tables2 import SingleTableView
from django.shortcuts import render, HttpResponse
from django.utils.safestring import mark_safe
from django.views import View

from interview.models import Interview, InterviewServerConfig
from interview.util import build_interview_full_name
from tenant.models import Tenant
from tenant.mixins import TenantAwareViewMixin
from school.models import SchoolUnit
from util.mongo_util import (
    create_dynamic_document_class,
    mongo_to_hierarchical_dict,
)
from util.file_import import is_metadata_valid, is_content_valid

from .util import custom_class_name, dict_to_docassemble_objects
from .forms import BulkDocumentGenerationForm
from .models import Document, BulkDocumentGeneration, DocumentTaskView, Signer, DocumentStatus, DocumentFileKind
# https://docs.celeryproject.org/en/latest/userguide/tasks.html#task-naming-relative-imports
from document.tasks import celery_create_document, celery_submit_to_esignature, celery_send_email, create_secret
from .tables import BulkDocumentGenerationTable, DocumentTaskViewTable, DocumentTable

logger = logging.getLogger(__name__)


DOCUMENT_COLUMNS = (
    (0, 'id'),
    (1, 'name'),
    (2, 'interview'),
    (3, 'school'),
    (4, 'created_date'),
    (5, 'altered_date'),
    (6, 'status'),
    (7, 'submit_to_esignature'),
    (8, 'send_email'),
)


class MultipleFieldLookupMixin(generics.GenericAPIView):
    def __init__(self):
        if not hasattr(self, 'lookup_fields'):
            raise AssertionError("Expected view {} to have `.lookup_fields` attribute".format(self.__class__.__name__))

    def get_object(self):
        for field in self.lookup_fields:
            if field in self.kwargs:
                self.lookup_field = field
                break
        else:
            raise AssertionError(
                'Expected view %s to be called with one of the lookup_fields: %s' %
                (self.__class__.__name__, self.lookup_fields))

        return super().get_object()


class DocumentDetailView(LoginRequiredMixin, TenantAwareViewMixin, MultipleFieldLookupMixin, DetailView):
    model = Document
    context_object_name = "document"
    lookup_fields = ('pk', 'doc_uuid')

    def get_context_data(self, **kwargs):
        if 'doc_uuid' in self.kwargs:
            document = Document.objects.get(doc_uuid=self.kwargs["doc_uuid"])
        else:
            document = Document.objects.get(pk=self.kwargs["pk"])

        context = super().get_context_data(**kwargs)

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
                ) order by s1.created_date desc;""".format(document_id=document.id))
        except:
            pass
        else:
            context['signers'] = list(signers)
            context['docx_file'] = document.get_docx_file()
            context['related_documents'] = document.get_related_documents()
            signer_statuses = list()
            for signer in signers:
                signer_statuses.append(signer.status)

            # Explicitly mark a string as safe for (HTML) output purposes. The returned object can be used
            # everywhere a string is appropriate.
            # https://docs.djangoproject.com/en/3.0/ref/utils/#django.utils.safestring.mark_safe
            # retorna uma lista com os status dos signatarios
            context['signer_statuses'] = mark_safe(signer_statuses)

        return context


class DocumentListView(LoginRequiredMixin, TenantAwareViewMixin, ListView):
    model = Document
    context_object_name = "documents"


class BulkDocumentGenerationDetailView(LoginRequiredMixin, TenantAwareViewMixin, SingleTableView):
    model = DocumentTaskView
    table_class = DocumentTaskViewTable
    context_table_name = "task_table"
    context_object_name = "document_tasks"
    template_name = "document/bulkdocumentgeneration_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "bulk_document_generation_id" in self.kwargs:
            bulk_generation = BulkDocumentGeneration.objects.get(
                pk=self.kwargs["bulk_document_generation_id"])
            documents = Document.objects.filter(bulk_generation=bulk_generation)
            context['bulk_document_generation'] = bulk_generation
            context['document_table'] = DocumentTable(documents)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        if "bulk_document_generation_id" in self.kwargs:
            return queryset.filter(bulk_generation=self.kwargs["bulk_document_generation_id"])
        else:
            return queryset


class BulkDocumentGenerationListView(LoginRequiredMixin, TenantAwareViewMixin, SingleTableView):
    model = BulkDocumentGeneration
    table_class = BulkDocumentGenerationTable
    context_object_name = "bulk_document_generations"


class ValidateCSVFile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = BulkDocumentGenerationForm()
        interview = Interview.objects.get(pk=self.kwargs["interview_id"])
        return render(
            request,
            "document/bulkdocumentgeneration_validate_generate.html",
            {
                "form": form,
                "interview_id": interview.pk,
                "data_valid": False,
                "validation_error": False,
            },
        )

    def post(self, request, *args, **kwargs):
        form = BulkDocumentGenerationForm(request.POST, request.FILES)
        if form.is_valid():
            # Consulta dados do aplicativo necessarios as validacoes
            interview = Interview.objects.get(pk=self.kwargs["interview_id"])
            source_file = request.FILES["source_file"]

            logger.info("Carregado o arquivo: " + source_file.name)

            # Transforma o arquivo CSV em um dataframe
            bulk_data = pd.read_csv(source_file, sep="#")

            try:
                # Valida os metadados do CSV (tipos de campos e flags booleanas)
                # Se os dados forem validos, retorna dois dicionarios: o de tipos de campos e
                # os de obrigatoriedade dos registros
                # Ambos são usados para criar a classe dinamica
                (
                    field_types_dict,
                    required_fields_dict,
                    metadata_valid,
                ) = is_metadata_valid(bulk_data)

            except ValueError as e:
                message = str(type(e).__name__) + " : " + str(e)
                messages.error(request, message)
                logger.error(message)

                return render(
                    request,
                    "document/bulkdocumentgeneration_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "data_valid": False,
                    },
                )

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
                    bulk_data_content,
                    parent_fields_dict,
                    error_messages,
                    content_valid,
                ) = is_content_valid(bulk_data)
            except ValueError as e:
                message = str(type(e).__name__) + " : " + str(e)
                messages.error(request, message)
                logger.error(message)

                return render(
                    request,
                    "document/bulkdocumentgeneration_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "data_valid": False,
                    },
                )

            if not content_valid:
                for message in error_messages:
                    messages.error(request, message)

                return render(
                    request,
                    "document/bulkdocumentgeneration_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "data_valid": False,
                    },
                )

            # Se houver registro invalido, esta variavel sera definida como False ao final da funcao.
            # Esta variavel ira modifica a logica de exibicao das telas ao usuario:
            # Se o CSV for valido, i.e., tiver todos os registros validos, sera exibida a tela de envio
            # Se nao, exibe as mesnagens de sucesso e de erro na tela de carregar novamente o CSV
            data_valid = metadata_valid and content_valid

            bulk_generation_id, mongo_document = validate_data_mongo(
                self.request, interview.pk, data_valid, bulk_data_content,
                field_types_dict, required_fields_dict, parent_fields_dict, True
            )

            if data_valid:
                return render(
                    request,
                    "document/bulkdocumentgeneration_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "data_valid": data_valid,
                        "bulk_generation_id": bulk_generation_id,
                    },
                )

            else:
                # TODO Testar se realmente apaga quando há erro Apaga a colecao do banco
                mongo_document.drop_collection()
                return render(
                    request,
                    "document/bulkdocumentgeneration_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "data_valid": data_valid,
                    },
                )


@login_required
def generate_bulk_documents(request, bulk_document_generation_id):
    bulk_document_generation = BulkDocumentGeneration.objects.get(pk=bulk_document_generation_id)
    logger.info(
        "Usando a classe bulk_generation: {dynamic_document_class_name}".format(
            dynamic_document_class_name=bulk_document_generation.mongo_db_collection_name
        )
    )
    dynamic_document_class = create_dynamic_document_class(
        bulk_document_generation.mongo_db_collection_name,
        bulk_document_generation.field_types_dict,
        bulk_document_generation.required_fields_dict,
        bulk_document_generation.parent_fields_dict,
        school_names_set=list(bulk_document_generation.school_names_set),
        school_units_names_set=list(bulk_document_generation.school_units_names_set),
    )

    try:
        success, data = generate_document_from_mongo(
            request, dynamic_document_class, bulk_document_generation.interview.pk)

        if success:
            bulk_document_generation.status = "em andamento..."

            bulk_document_generation.save()

            payload = {
                "success": True,
                "total_task_size": data,
                "bulk_status": bulk_document_generation.status,
                "message": "A tarefa foi enviada para execução"
            }
        else:
            payload = {
                "success": False,
                "message": str(data),
            }

        return HttpResponse(json.dumps(payload), content_type="application/json")
    except Exception as e:
        error_message = "Houve erro no processo de geração em lote. | {exc}".format(exc=str(type(e).__name__) + " : " + str(e))
        logger.error(error_message)

        payload = {
            "success": False,
            "message":  error_message,
        }

        return HttpResponse(json.dumps(payload), content_type="application/json")


def generate_document_from_mongo(request, dynamic_document_class, interview_id, mongo_document_id=None):
    if mongo_document_id:
        mongo_documents_collection = dynamic_document_class.objects.filter(id=mongo_document_id)
    else:
        mongo_documents_collection = dynamic_document_class.objects

    logger.info(
        "Recuperados {n} documento(s) do Mongo".format(n=len(mongo_documents_collection))
    )

    # gera lista de documentos em lista de dicionarios
    hierarchical_dict_list = list()
    for mongo_document in mongo_documents_collection:
        hierarchical_dict = mongo_to_hierarchical_dict(mongo_document)
        hierarchical_dict_list.append(hierarchical_dict)

    logger.info(
        "Gerados {n} dicionários hierárquicos.".format(n=len(hierarchical_dict_list))
    )

    interview = Interview.objects.get(pk=interview_id)
    tenant = request.user.tenant

    interview_variables_list = dict_to_docassemble_objects(
        hierarchical_dict_list, interview.document_type.pk
    )

    isc = InterviewServerConfig.objects.get(interviews=interview.pk)
    base_url = isc.base_url
    api_key = isc.user_key
    username = isc.username
    user_password = isc.user_password

    # monta nome da entrevista de acordo com especificações do docassemble
    interview_full_name = build_interview_full_name(
        isc.user_id, isc.project_name, interview.yaml_name, "interview_filename",
    )

    logger.info(
        "Nome da entrevista: {interview_full_name} ".format(
            interview_full_name=interview_full_name
        )
    )

    url_args = {
        "tid": request.user.tenant.pk,
        "ut": request.user.auth_token.key,
        "intid": interview.pk,
    }

    # TODO continua chamando API para interview data (nao sei pq) e para school (ainda nao feita)
    interview_data = {
        "id": interview.pk,
        "name": interview.name,
        "version": interview.version,
        "date_available": str(interview.date_available),
        "description": interview.description,
        "language": interview.language,
        "custom_file_name": interview.custom_file_name,
        "is_generic": interview.is_generic,
        "is_freemium": interview.is_freemium,
        "yaml_name": interview.yaml_name,
        "document_type": interview.document_type.pk,
    }

    plan_data = {
        "use_esignature": tenant.plan.use_esignature,
        "use_ged": tenant.plan.use_ged,
    }

    tenant_ged_data = {
        "url": tenant.tenantgeddata.url,
        "token": tenant.tenantgeddata.token,
    }

    tenant_esignature_data = {
        "provider": tenant.esignature_app.provider,
        "private_key": tenant.esignature_app.private_key,
        "client_id": tenant.esignature_app.client_id,
        "impersonated_user_guid": tenant.esignature_app.impersonated_user_guid,
        "test_mode": tenant.esignature_app.test_mode,
    }

    try:
        secret = create_secret(base_url, api_key, username, user_password)

        total_task_size = 0

        for i, interview_variables in enumerate(interview_variables_list):
            # Recupera o registro do documento no Educa Legal e passa o doc_uuid como url_args
            try:
                el_document = Document.objects.get(mongo_uuid=interview_variables["mongo_uuid"])
            except Document.DoesNotExist:
                return False, 'Não foi encontrado o documento com mongo_uuid = {}'.format(
                    interview_variables["mongo_uuid"])
            url_args["doc_uuid"] = str(el_document.doc_uuid)
            interview_variables["url_args"] = url_args
            interview_variables["interview_data"] = interview_data
            interview_variables["plan_data"] = plan_data
            interview_variables["tenant_ged_data"] = tenant_ged_data
            interview_variables["tenant_esignature_data"] = tenant_esignature_data
            logger.info(
                "Enviando documento {n} de {t}".format(
                    n=str(i + 1), t=len(interview_variables_list)
                )
            )

            # Se for enviar para assinatura eletrônica nao enviar por e-mail
            if interview_variables["submit_to_esignature"]:
                interview_variables["el_send_email"] = False

            if interview_variables["submit_to_esignature"]:

                # result = celery_create_document(
                #         base_url,
                #         api_key,
                #         secret,
                #         interview_full_name,
                #         interview_variables
                #     )
                #
                # celery_submit_to_esignature(str(el_document.doc_uuid))

                result = chain(
                    # nao é necessario passar o self, é passado automaticamente
                    celery_create_document.s(
                        base_url,
                        api_key,
                        secret,
                        interview_full_name,
                        interview_variables
                    ),
                    # o retorno da primeira função é passado automaticamente para a segunda como 2o parametro
                    # porque estão encadeados com o chain, por isso não é necessário passar o doc_uuid
                    # https://docs.celeryproject.org/en/stable/userguide/canvas.html#chains
                    celery_submit_to_esignature.s(),
                )()
                result_description = "Criação do documento: {parent_id} | Assinatura: {child_id}".format(
                    parent_id=result.parent.id, child_id=result.id)

                # faz refresh pq alguns campos sao atualizados nas funcoes que o celery chama
                el_document.refresh_from_db()
                el_document.task_create_document = result.parent.id
                el_document.task_submit_to_esignature = result.id
                total_task_size += 2
            elif interview_variables["el_send_email"]:

                # result = celery_create_document(
                #         base_url,
                #         api_key,
                #         secret,
                #         interview_full_name,
                #         interview_variables
                #     )
                #
                # celery_send_email(str(el_document.doc_uuid))

                result = chain(
                    # nao é necessario passar o self, é passado automaticamente
                    celery_create_document.s(
                        base_url,
                        api_key,
                        secret,
                        interview_full_name,
                        interview_variables
                    ),
                    # o retorno da primeira função é passado automaticamente para a segunda como 2o parametro
                    # porque estão encadeados com o chain, por isso não é necessário passar o doc_uuid
                    # https://docs.celeryproject.org/en/stable/userguide/canvas.html#chains
                    celery_send_email.s(),
                )()
                result_description = "Criação do documento: {parent_id} | Envio por e-mail: {child_id}".format(
                    parent_id=result.parent.id, child_id=result.id)

                # faz refresh pq alguns campos sao atualizados nas funcoes que o celery chama
                el_document.refresh_from_db()
                el_document.task_create_document = result.parent.id
                el_document.task_send_email = result.id
                total_task_size += 2
            else:
                result = celery_create_document.delay(
                    base_url,
                    api_key,
                    secret,
                    interview_full_name,
                    interview_variables
                )
                result_description = "Criação do documento: {id}".format(id=result.id)

                # faz refresh pq alguns campos sao atualizados nas funcoes que o celery chama
                el_document.refresh_from_db()
                el_document.task_create_document = result.id
                total_task_size += 1

            request.session["total_task_size"] = total_task_size

            el_document.save()
            logger.info(result_description)

        return True, total_task_size
    except Exception as e:
        return False, e


@login_required
def bulk_generation_progress(request, bulk_document_generation_id):
    document_task_view = DocumentTaskView.objects.filter(bulk_generation_id=bulk_document_generation_id)
    bulk_document_generation = BulkDocumentGeneration.objects.get(pk=bulk_document_generation_id)

    # Como as tarefas sao passadas assincronamente para o Celery, há um atraso até que a tabela de tarefas seja carregada.
    # por isso é necessário iniciar as variáveis com 0 e perguntar pelo tamanho da lista de tarefas
    processed_task_size = 0
    success_task_size = 0
    failure_task_size = 0

    if len(document_task_view) > 0:
        success_task_size = len([x for x in document_task_view if x.task_status == "SUCCESS"])
        failure_task_size = len([x for x in document_task_view if x.task_status == "FAILURE"])
        processed_task_size = success_task_size + failure_task_size

    # A quantidade total de tarefas é armazenada na seção na função generate_bulk_documents
    if request.session["total_task_size"] == processed_task_size:
        if request.session["total_task_size"] == success_task_size:
            bulk_document_generation.status = "concluída com sucesso"
        if request.session["total_task_size"] > success_task_size:
            bulk_document_generation.status = "concluída com erros"
        bulk_document_generation.save()
        del request.session["total_task_size"]

    payload = {
        "processed_task_size": processed_task_size,
        "success_task_size": success_task_size,
        "failure_task_size": failure_task_size,
        "bulk_status": bulk_document_generation.status
    }
    logger.info(payload)

    return HttpResponse(json.dumps(payload), content_type="application/json")


def query_documents_by_args(pk=None, **kwargs):
    draw = int(kwargs.get('draw', None)[0])
    length = int(kwargs.get('length', None)[0])
    start = int(kwargs.get('start', None)[0])
    search_value = kwargs.get('search[value]', None)[0]
    order_column = int(kwargs.get('order[0][column]', None)[0])
    order = kwargs.get('order[0][dir]', None)[0]

    order_column = DOCUMENT_COLUMNS[order_column]
    # django orm '-' -> desc
    if order == 'desc':
        order_column = '-' + order_column[1]
    else:
        order_column = order_column[1]

    queryset = Document.objects.filter(tenant=pk, parent=None)
    total = queryset.count()

    if search_value:
        if search_value == 'não' or search_value == 'nao':
            boolean_search_value = False
        elif search_value == 'sim':
            boolean_search_value = True
        try:
            if boolean_search_value or not boolean_search_value:
                queryset = queryset.filter(Q(name__unaccent__icontains=search_value) |
                                           Q(interview__name__unaccent__icontains=search_value) |
                                           Q(school__name__unaccent__icontains=search_value) |
                                           Q(status__unaccent__icontains=search_value) |
                                           Q(submit_to_esignature=boolean_search_value) |
                                           Q(send_email=boolean_search_value))
        except NameError:
            queryset = queryset.filter(Q(name__unaccent__icontains=search_value) |
                                       Q(interview__name__unaccent__icontains=search_value) |
                                       Q(school__name__unaccent__icontains=search_value) |
                                       Q(status__unaccent__icontains=search_value))

    count = queryset.count()
    queryset = queryset.order_by(order_column)[start:start + length]
    data = {
        'items': queryset,
        'count': count,
        'total': total,
        'draw': draw,
    }
    return data


def save_document_data(document, url, file_data, relative_path, has_ged, ged_data, filename, parent=None):
    if has_ged:
        document.ged_id = ged_data['id']
        document.ged_link = ged_data['latest_version']['document_url'] + 'download/'
        document.ged_uuid = ged_data['uuid']

    if url:
        try:
            # salva como arquivo temporario
            temp_file, _ = urlretrieve(url)
            # salva arquivo na nuvem (campo file esta configurado pra salvar no spaces)
            document.cloud_file.save(relative_path + filename, File(open(temp_file, 'rb')))
        except Exception as e:
            message = 'Erro ao fazer o upload do documento na nuvem. Erro: {e}'.format(e=e)
            logging.error(message)
        finally:
            # apaga arquivo temporario
            urlcleanup()
    else:
        try:
            file = ContentFile(file_data, name=filename)
            document.cloud_file.save(relative_path + filename, file)
        except Exception as e:
            message = 'Erro ao fazer o upload do documento na nuvem. Erro: {e}'.format(e=e)
            logging.error(message)

    document.status = DocumentStatus.INSERIDO_GED.value

    if parent:
        # cria documento relacionado ao documento pdf principal
        document.doc_uuid = uuid.uuid4()
        document.parent = parent

        try:
            # salva dados do ged do documento no educa legal
            document.save()
        except Exception as e:
            message = 'Não foi possível salvar o documento no sistema. {}'.format(str(e))
            logging.exception(message)
    else:
        document.file_kind = DocumentFileKind.PDF.value

        try:
            if has_ged:
                # salva dados do ged do documento no educa legal
                document.save(update_fields=['ged_id', 'ged_link', 'ged_uuid', 'status', 'file_kind'])
            else:
                # salva dados do ged do documento no educa legal
                document.save(update_fields=['status', 'file_kind'])
        except Exception as e:
            message = 'Não foi possível salvar o documento no sistema. {}'.format(str(e))
            logging.exception(message)


def validate_data_mongo(request, interview_id, data_valid, bulk_data_content,
                        field_types_dict, required_fields_dict, parent_fields_dict, is_bulk_generation):
    tenant = Tenant.objects.get(pk=request.user.tenant_id)
    interview = Interview.objects.get(pk=interview_id)
    schools = tenant.school_set.all()
    # Monta os conjuntos de nomes de escolas e de unidades escolares para validacao
    school_units_names_set = set()
    for school in schools:
        school_units = SchoolUnit.objects.filter(school=school).values_list(
            "name", flat=True
        )
        for school_unit in school_units:
            school_units_names_set.add(school_unit)
    school_names_set = set(schools.values_list("name", flat=True))
    # Adiciona como elemento valido "---" para ausencia de unidade escolar
    school_units_names_set.add("---")

    # O nome da collection deve ser unico no Mongo, pq cada collection representa uma acao
    # de importação. Precisaremos do nome da collection depois para recuperá-la do Mongo
    # O nome gerado e semelhante ao custom file name que usamos no docassemble
    # YYYYMMDD_HHMMSS_custom_file_name
    if is_bulk_generation:
        dynamic_document_class_name = (custom_class_name(interview.custom_file_name))
    else:
        dynamic_document_class_name = 'api_' + interview.custom_file_name

    # Cria a classe do tipo Document (mongoengine) dinamicamente
    dynamic_document_class = create_dynamic_document_class(
        dynamic_document_class_name,
        field_types_dict,
        required_fields_dict,
        parent_fields_dict,
        school_names_set=school_names_set,
        school_units_names_set=school_units_names_set,
    )

    # Percorre o df resultante, que possui apenas o conteudo e tenta gravar cada uma das linhas
    # no Mongo
    mongo_document_data_list = list()
    mongo_document = None

    for register_index, row in enumerate(
            bulk_data_content.itertuples(index=False)
    ):
        # Transforma a linha em dicionario
        row_dict = row._asdict()
        # Cria um objeto Documento a partir da classe dinamica
        mongo_document = dynamic_document_class(**row_dict)

        try:
            mongo_document_data = mongo_document.save()
            mongo_document_data_list.append(mongo_document_data)
            # Se a operacao for bem sucedida, itera sobre a lista de valores para gerar a
            # mensagem de sucesso
            row_values = list(row_dict.values())
            message = "Registro {register_index} validado com sucesso".format(
                register_index=str(register_index + 1)
            )
            for value_index, value in enumerate(row_values):
                message += " | " + str(row_values[value_index])
            logger.info(message)
            messages.success(request, message)
        except ValidationError as e:
            # Se a operacao for mal sucedida, itera sobre a lista de valores para gerar a
            # mensagem de erro
            row_values = list(row_dict.values())
            message = (
                    "Erro ao validar o registro "
                    + str(register_index + 1)
                    + ": "
                    + str(e)
            )
            for value_index, value in enumerate(row_values):
                message += " | " + str(row_values[value_index])
            logger.info(message)
            messages.error(request, message)

    storage = get_messages(request)
    for message in storage:
        if message.level_tag == "error":
            data_valid = False
            break

    if data_valid:
        if is_bulk_generation:
            bulk_generation = BulkDocumentGeneration(
                tenant=request.user.tenant,
                interview=interview,
                mongo_db_collection_name=dynamic_document_class_name,
                field_types_dict=field_types_dict,
                required_fields_dict=required_fields_dict,
                parent_fields_dict=parent_fields_dict,
                school_names_set=list(school_names_set),
                school_units_names_set=list(school_units_names_set),
                status="não executada"
            )
            bulk_generation.save()

            interview_name = interview.name + "-rascunho-em-lote"
        else:
            interview_name = interview.name
            bulk_generation = None

        el_document_list = list()
        for mongo_document_data in mongo_document_data_list:
            school = tenant.school_set.filter(name=mongo_document_data.selected_school)[0]
            el_document = Document(
                tenant=tenant,
                name=interview_name,
                status=DocumentStatus.RASCUNHO.value,
                description=interview.description + " | " + interview.version + " | " + str(interview.date_available),
                interview=interview,
                school=school,
                bulk_generation=bulk_generation,
                mongo_uuid=str(mongo_document_data.id),
                submit_to_esignature=mongo_document_data.submit_to_esignature,
                send_email=mongo_document_data.el_send_email
            )
            el_document_list.append(el_document)

        Document.objects.bulk_create(el_document_list)

        logger.info(
            "Gravada a estrutura de classe bulk_generation: {dynamic_document_class_name}".format(
                dynamic_document_class_name=dynamic_document_class_name
            )
        )

        if is_bulk_generation:
            return bulk_generation.pk, mongo_document
        else:
            return mongo_document, dynamic_document_class_name, school_names_set, school_units_names_set


def reached_document_limit(tenant_id):
    today = datetime.today()

    # verifica se atingiu o limite de documentos
    tenant = Tenant.objects.get(pk=tenant_id)
    documents = Document.objects.filter(tenant=tenant,
                                        created_date__month=today.month,
                                        created_date__year=today.year)

    if tenant.has_ged():
        document_count = documents.exclude(Q(status="rascunho") | Q(status="criado")).count()
    else:
        document_count = documents.exclude(status="rascunho").count()

    reached_limit = False
    if tenant.plan.document_limit:
        if document_count >= tenant.plan.document_limit:
            reached_limit = True

    return reached_limit, tenant.plan.document_limit
