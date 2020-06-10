import logging
import pandas as pd
from mongoengine.errors import ValidationError
from celery import chain

from django.views.generic.detail import DetailView
from django_tables2 import SingleTableView
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View

from tenant.models import Tenant
from tenant.mixins import TenantAwareViewMixin
from school.models import SchoolUnit
from interview.models import Interview, InterviewServerConfig
from interview.util import build_interview_full_name
from document.models import Document
from document.tables import DocumentTable
from util.mongo_util import (
    create_dynamic_document_class,
    mongo_to_hierarchical_dict,
)

from util.file_import import is_csv_metadata_valid, is_csv_content_valid
from .util import custom_class_name, dict_to_docassemble_objects, create_secret
from .forms import BulkDocumentGenerationForm
from .models import BulkDocumentGeneration
from .tasks import create_document, submit_to_esignature
from .tables import BulkDocumentGenerationTable

logger = logging.getLogger(__name__)


class DocumentDetailView(LoginRequiredMixin, TenantAwareViewMixin, DetailView):
    model = Document
    context_object_name = "document"


class DocumentListView(LoginRequiredMixin, TenantAwareViewMixin, SingleTableView):
    model = Document
    table_class = DocumentTable
    context_object_name = "documents"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "bulk_document_generation_id" in self.kwargs:
            context['bulk_document_generation'] = BulkDocumentGeneration.objects.get(pk=self.kwargs["bulk_document_generation_id"])
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
            "document/bulkinterview_validate_generate.html",
            {
                "form": form,
                "interview_id": interview.pk,
                "csv_valid": False,
                "validation_error": False,
            },
        )

    def post(self, request, *args, **kwargs):
        form = BulkDocumentGenerationForm(request.POST, request.FILES)
        if form.is_valid():
            # Consulta dados do aplicativo necessarios as validacoes
            interview = Interview.objects.get(pk=self.kwargs["interview_id"])
            tenant = Tenant.objects.get(pk=self.request.user.tenant_id)
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
                    csv_metadata_valid,
                ) = is_csv_metadata_valid(bulk_data)

            except ValueError as e:
                message = str(type(e).__name__) + " : " + str(e)
                messages.error(request, message)
                logger.error(message)

                return render(
                    request,
                    "document/bulkinterview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "csv_valid": False,
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
                    csv_content_valid,
                ) = is_csv_content_valid(bulk_data)
            except ValueError as e:
                message = str(type(e).__name__) + " : " + str(e)
                messages.error(request, message)
                logger.error(message)

                return render(
                    request,
                    "document/bulkinterview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "csv_valid": False,
                    },
                )

            if not csv_content_valid:
                for message in error_messages:
                    messages.error(request, message)

                return render(
                    request,
                    "document/bulkinterview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "csv_valid": False,
                    },
                )

            # Se houver registro invalido, esta variavel sera definida como False ao final da funcao.
            # Esta variavel ira modifica a logica de exibicao das telas ao usuario:
            # Se o CSV for valido, i.e., tiver todos os registros validos, sera exibida a tela de envio
            # Se nao, exibe as mesnagens de sucesso e de erro na tela de carregar novamente o CSV
            csv_valid = csv_metadata_valid and csv_content_valid

            # O nome da collection deve ser unico no Mongo, pq cada collection representa uma acao
            # de importação. Precisaremos do nome da collection depois para recuperá-la do Mongo
            # O nome gerado e semelhante ao custom file name que usamos no docassemble
            # YYYYMMDD_HHMMSS_custom_file_name
            dynamic_document_class_name = (custom_class_name(interview.custom_file_name))

            # Cria a classe do tipo Document (mongoengine) dinamicamente
            DynamicDocumentClass = create_dynamic_document_class(
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

            for register_index, row in enumerate(
                bulk_data_content.itertuples(index=False)
            ):
                # Transforma a linha em dicionario
                row_dict = row._asdict()
                # Cria um objeto Documento a partir da classe dinamica
                mongo_document = DynamicDocumentClass(**row_dict)

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
                    csv_valid = False
                    break

            if csv_valid:
                bulk_generation = BulkDocumentGeneration(
                    tenant=request.user.tenant,
                    interview=interview,
                    mongo_db_collection_name=dynamic_document_class_name,
                    field_types_dict=field_types_dict,
                    required_fields_dict=required_fields_dict,
                    parent_fields_dict=parent_fields_dict,
                    school_names_set=list(school_names_set),
                    school_units_names_set=list(school_units_names_set),
                )
                bulk_generation.save()

                el_document_list = list()
                for mongo_document_data in mongo_document_data_list:
                    school = tenant.school_set.filter(name=mongo_document_data.selected_school)[0]
                    el_document = Document(
                        tenant=tenant,
                        name=interview.name + " - rascunho",
                        status="rascunho",
                        description=interview.description + " | " + interview.version + " | " + str(interview.date_available),
                        interview=interview,
                        school=school,
                        bulk_generation=bulk_generation,
                        mongo_id=mongo_document_data.id,
                        submit_to_esignature=mongo_document_data.submit_to_esignature
                    )
                    el_document_list.append(el_document)

                Document.objects.bulk_create(el_document_list)

                logger.info(
                    "Gravada a estrutura de classe bulk_generation: {dynamic_document_class_name}".format(
                        dynamic_document_class_name=dynamic_document_class_name
                    )
                )

                return render(
                    request,
                    "document/bulkinterview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "csv_valid": csv_valid,
                        "bulk_generation_id": bulk_generation.pk,
                    },
                )

            else:
                # TODO Testar se realmente apaga quando há erro Apaga a colecao do banco
                mongo_document.drop_collection()
                return render(
                    request,
                    "document/bulkinterview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "csv_valid": csv_valid,
                    },
                )


@login_required
def generate_bulk_documents(request, bulk_interview_id):
    bulk_generation = BulkDocumentGeneration.objects.get(pk=bulk_interview_id)
    logger.info(
        "Usando a classe bulk_generation: {dynamic_document_class_name}".format(
            dynamic_document_class_name=bulk_generation.mongo_db_collection_name
        )
    )
    interview = Interview.objects.get(pk=bulk_generation.interview.pk)
    tenant = request.user.tenant
    DynamicDocumentClass = create_dynamic_document_class(
        bulk_generation.mongo_db_collection_name,
        bulk_generation.field_types_dict,
        bulk_generation.required_fields_dict,
        bulk_generation.parent_fields_dict,
        school_names_set=list(bulk_generation.school_names_set),
        school_units_names_set=list(bulk_generation.school_units_names_set),
    )

    mongo_documents_collection = DynamicDocumentClass.objects

    # gera lista de documentos em lista de dicionarios
    hierarchical_dict_list = list()
    for mongo_document in mongo_documents_collection:
        hierarchical_dict = mongo_to_hierarchical_dict(mongo_document)

        hierarchical_dict_list.append(hierarchical_dict)

    # documents_collection = list(documents_collection)
    logger.info(
        "Recuperados {n} documento(s) do Mongo".format(n=len(mongo_documents_collection))
    )

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
        "Servidor e nome da entrevista: {interview_full_name} ".format(
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
        "provider": tenant.tenantesignaturedata.provider,
        "private_key": tenant.tenantesignaturedata.private_key,
        "client_id": tenant.tenantesignaturedata.client_id,
        "impersonated_user_guid": tenant.tenantesignaturedata.impersonated_user_guid,
        "test_mode": tenant.tenantesignaturedata.test_mode,
    }

    results_list = list()
    try:
        secret = create_secret(base_url, api_key, username, user_password)

        for i, interview_variables in enumerate(interview_variables_list):
            interview_variables["url_args"] = url_args
            interview_variables["interview_data"] = interview_data
            interview_variables["plan_data"] = plan_data
            interview_variables["tenant_ged_data"] = tenant_ged_data
            interview_variables["tenant_esignature_data"] = tenant_esignature_data
            logger.info(
                "Enviando tarefa {n} de {t}".format(
                    n=str(i + 1), t=len(interview_variables_list)
                )
            )

            el_document = Document.objects.get(mongo_id=interview_variables["mongo_id"])

            if interview_variables["submit_to_esignature"]:
                result = chain(
                    create_document.s(
                        base_url,
                        api_key,
                        secret,
                        interview_full_name,
                        interview_variables,
                    ),
                    submit_to_esignature.s(
                        base_url, api_key, secret, interview_full_name
                    ),
                )()
                result_description = "Criação do documento: {parent_id} | Assinatura: {child_id}".format(parent_id=result.parent.id, child_id=result.id)
                el_document.task_create_document = result.parent.id
                el_document.task_submit_to_esignature = result.id

            else:
                result = create_document.delay(
                    base_url, api_key, secret, interview_full_name, interview_variables,
                )
                result_description = "Criação do documento: {id}".format(id=result.id)
                el_document.task_create_document = result.id
            el_document.save()
            logger.info(result_description)

    except Exception as e:
        message = "Houve erro no processo de geração em lote. | {exc}".format(exc=str(type(e).__name__) + " : " + str(e))
        logger.error(message)
        messages.error(request, message)

    return DocumentListView.as_view()(request, bulk_document_generation_id=bulk_generation.pk)