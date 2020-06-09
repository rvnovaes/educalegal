import logging
import uuid
from enum import Enum
from celery import chain
from mongoengine import ValidationError
import pandas as pd
from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError

from django.conf import settings
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views import View

from tenant.models import Tenant
from school.models import School, SchoolUnit
from interview.models import Interview, InterviewServerConfig
from interview.util import build_interview_full_name
from document.models import Document
from bulk_import_util.mongo_util import (
    create_mongo_connection,
    create_dynamic_document_class,
    mongo_to_hierarchical_dict,
)
from bulk_import_util.file_import import is_csv_metadata_valid, is_csv_content_valid

from .docassemble_client import DocassembleClient, DocassembleAPIException
from .forms import BulkInterviewForm
from .models import BulkGeneration
from .docassemble_client import DocassembleAPIException
from .tasks import create_document, submit_to_esignature

create_mongo_connection(
    settings.MONGO_DB,
    settings.MONGO_ALIAS,
    settings.MONGO_USERNAME,
    settings.MONGO_PASSWORD,
    settings.MONGO_HOST,
    settings.MONGO_PORT,
)

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    DEBUG_BULK = 1
    PRESTACAO_SERVICOS_ESCOLARES = 2
    ACORDOS_TRABALHISTAS_INDIVIDUAIS = 37


class ValidateCSVFile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = BulkInterviewForm()
        interview = Interview.objects.get(pk=self.kwargs["interview_id"])
        return render(
            request,
            "bulk_interview/bulk_interview_validate_generate.html",
            {
                "form": form,
                "interview_id": interview.pk,
                "csv_valid": False,
                "validation_error": False,
            },
        )

    def post(self, request, *args, **kwargs):
        form = BulkInterviewForm(request.POST, request.FILES)
        if form.is_valid():
            # Consulta dados do aplicativo necessarios as validacoes
            interview = Interview.objects.get(pk=self.kwargs["interview_id"])
            tenant = Tenant.objects.get(pk=self.request.user.tenant_id)
            schools = School.objects.filter(tenant=tenant)
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
                    "bulk_interview/bulk_interview_validate_generate.html",
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
                    "bulk_interview/bulk_interview_validate_generate.html",
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
                    "bulk_interview/bulk_interview_validate_generate.html",
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
            # uuid4 gera um UUID aleatorio
            dynamic_document_class_name = (
                interview.custom_file_name + "_bulk_" + str(uuid.uuid4())
            )

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
            mongo_documents_list = list()

            for register_index, row in enumerate(
                bulk_data_content.itertuples(index=False)
            ):
                # Transforma a linha em dicionario
                row_dict = row._asdict()
                # Cria um objeto Documento a partir da classe dinamica
                dynamic_document = DynamicDocumentClass(**row_dict)

                try:
                    document_data = dynamic_document.save()
                    mongo_documents_list.append(document_data)
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
                bulk_generation = BulkGeneration(
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

                for document_data in mongo_documents_list:
                    el_document = Document(
                        name=""

                    )


                logger.info(
                    "Gravada a estrutura de classe bulk_generation: {dynamic_document_class_name}".format(
                        dynamic_document_class_name=dynamic_document_class_name
                    )
                )

                return render(
                    request,
                    "bulk_interview/bulk_interview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "csv_valid": csv_valid,
                        "bulk_generation_id": bulk_generation.pk,
                    },
                )

            else:
                # TODO Testar se realmente apaga quando há erro Apaga a colecao do banco
                dynamic_document.drop_collection()
                return render(
                    request,
                    "bulk_interview/bulk_interview_validate_generate.html",
                    {
                        "form": form,
                        "interview_id": interview.pk,
                        "validation_error": True,
                        "csv_valid": csv_valid,
                    },
                )


@login_required
def generate_bulk_documents(request, bulk_generation_id):
    bulk_generation = BulkGeneration.objects.get(pk=bulk_generation_id)
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

    documents_collection = DynamicDocumentClass.objects

    # gera lista de documentos em lista de dicionarios
    documents_list = list()
    for document in documents_collection:
        document = mongo_to_hierarchical_dict(document)

        documents_list.append(document)

    # documents_collection = list(documents_collection)
    logger.info(
        "Recuperados {n} documento(s) do Mongo".format(n=len(documents_collection))
    )

    interview_variables_list = _dict_to_docassemble_objects(
        documents_list, interview.document_type.pk
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
        secret = _create_secret(base_url, api_key, username, user_password)

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
                results_list.append(result_description)
            else:
                result = create_document.delay(
                    base_url, api_key, secret, interview_full_name, interview_variables,
                )
                result_description = "Criação do documento: {id}".format(id=result.id)
                results_list.append(result_description)

    except Exception as e:
        message = "Houve erro no processo de geração em lote. | {exc}".format(exc=str(type(e).__name__) + " : " + str(e))
        logger.error(message)
        messages.error(request, message)

    return render(
        request,
        "bulk_interview/bulk_interview_generation_result.html",
        {"results_list": results_list},
    )


def _dict_to_docassemble_objects(documents, interview_type_id):
    interview_variables_list = list()

    for document in documents:
        logger.info(
            "Gerando lista de variáveis para o objeto {object_id}".format(
                object_id=str(document['id'])
            )
        )

        if interview_type_id == DocumentType.PRESTACAO_SERVICOS_ESCOLARES.value:
            # tipos de pessoa no contrato de prestacao de servicos
            person_types = ['students', 'contractors']

            for person in person_types:
                # cria hierarquia para endereço da pessoa
                _build_address_dict(document, person)

                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", person, 0)

                # Cria a representacao do objeto Address da pessoa
                _create_address_obj(document, person, 0)

            document["content_document"] = "contrato-prestacao-servicos-educacionais.docx"
        elif interview_type_id == DocumentType.ACORDOS_TRABALHISTAS_INDIVIDUAIS.value:
            pass

        # remove campos herdados do mongo e que nao existem na entrevista
        document.pop('id')
        document.pop('created')

        interview_variables_list.append(document)

        logger.info(
            "Criada lista variáveis de documentos a serem gerados em lote com {size} documentos.".format(
                size=len(interview_variables_list)
            )
        )

    return interview_variables_list


def _build_name_dict(document, parent):
    document[parent]["name"] = dict()
    document[parent]["name"]["text"] = document[parent]["name_text"]
    document[parent].pop("name_text")

    return document


def _build_address_dict(document, parent):
    address = dict()
    address_attributes = [
        "zip",
        "street_name",
        "street_number",
        "unit",
        "neighborhood",
        "city",
        "state"
    ]

    for attribute in address_attributes:
        address[attribute] = document[parent][attribute]
        document[parent].pop(attribute)

    document[parent]["address"] = address

    return document


def _dict_from_documents_old(documents_collection, interview_type_id):
    interview_variables_list = list()

    if interview_type_id == 37:

        for i, document in enumerate(documents_collection):
            logger.info(
                "Gerando lista de variáveis para o objeto {object_id}".format(
                    object_id=str(document.id)
                )
            )

            document = mongo_to_hierarchical_dict(document, [])

            worker = dict()
            worker_attributes = [
                "cpf",
                "rg",
                "nationality",
                "marital_status",
                "ctps",
                "serie",
                "email",
            ]

            for attribute in worker_attributes:
                # Se não houver o atributo no documento, ele estava em branco na planilha
                try:
                    worker[attribute] = document[attribute]
                    document.pop(attribute)
                except KeyError:
                    worker[attribute] = ""

            worker["instanceName"] = "workers[0]"
            worker["_class"] = "docassemble.base.util.Person"
            worker["name"] = dict()
            worker["name"]["_class"] = "docassemble.base.util.Name"
            worker["name"]["text"] = document["name_text"]
            worker["name"]["instanceName"] = "workers[0].name"
            document.pop("name_text")

            address = dict()
            address_attributes = [
                "zip",
                "street_name",
                "street_number",
                "complement",
                "neighborhood",
                "city",
                "state",
            ]

            for attribute in address_attributes:
                # Se não houver o atributo no documento, ele estava em branco na planilha
                try:
                    address[attribute] = document[attribute]
                    document.pop(attribute)
                except KeyError:
                    address[attribute] = ""

            worker["address"] = address
            worker["address"]["instanceName"] = "workers[0].address"
            worker["address"]["_class"] = "docassemble.base.util.Address"

            document["workers"] = dict()
            document["workers"]["elements"] = list()
            document["workers"]["elements"].append(worker)
            document["workers"]["auto_gather"] = "False"
            document["workers"]["gathered"] = "True"
            document["workers"]["_class"] = "docassemble.base.core.DAList"
            document["workers"]["instanceName"] = "workers"

            document["documents_list"] = dict()
            document["documents_list"]["_class"] = "docassemble.base.core.DADict"
            document["documents_list"]["ask_number"] = False
            document["documents_list"]["ask_object_type"] = False
            document["documents_list"]["auto_gather"] = False
            # document["documents_list"]["complete_attribute"] =  null,

            document["documents_list"]["elements"] = dict()
            if document["docmp9362020"] == "s":
                document["documents_list"]["elements"][
                    "acordo-individual-reducao-de-jornada-e-reducao-salarial-mp-936-2020.docx"
                ] = True
            else:
                document["documents_list"]["elements"][
                    "acordo-individual-reducao-de-jornada-e-reducao-salarial-mp-936-2020.docx"
                ] = False

            if document["docmp9272020"] == "s":
                document["documents_list"]["elements"][
                    "termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.docx"
                ] = True
            else:
                document["documents_list"]["elements"][
                    "termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.docx"
                ] = False

            if document["docdireitoautoral"] == "s":
                document["documents_list"]["elements"][
                    "termo-mudanca-de-regime-e-cessao-do-direito-autoral.docx"
                ] = True
            else:
                document["documents_list"]["elements"][
                    "termo-mudanca-de-regime-e-cessao-do-direito-autoral.docx"
                ] = False

            document["documents_list"]["gathered"] = True
            document["documents_list"]["instanceName"] = "documents_list"
            # document["documents_list"]["minimum_number"]: null,
            # document["documents_list"]["object_type"]: null,
            # document["documents_list"]["object_type_parameters"]: {}

            document[
                "content_document"
            ] = "acordos-individuais-trabalhistas-coronavirus.docx"
            document["valid_workers_table"] = "continue"

    return interview_variables_list


def _create_person_obj(document, person_type, person_list_name, index):
    """ Cria a representação da pessoa como objeto do Docassemble
        document
        person_type: f  - física
                     j  - jurídica
                     fj - ambos
        person_list_name - nome da lista da parte: contratantes, contratadas, locatárias, locadoras, etc.
        index - índice do elemento da lista que será convertido
    """
    # cria hierarquia para name do person_list_name
    _build_name_dict(document, person_list_name)

    person = document[person_list_name]

    if person_type == 'fj':
        person["_class"] = "docassemble.base.util.Person"
        person["name"]["_class"] = "docassemble.base.util.Name"
    elif person_type == 'f':
        person["_class"] = "docassemble.base.util.Individual"
        person["name"]["_class"] = "docassemble.base.util.IndividualName"
        person["name"]["uses_parts"] = True
    else:
        person["_class"] = "docassemble.base.util.Organization"
        person["name"]["_class"] = "docassemble.base.util.Name"

    person["instanceName"] = person_list_name + '[' + str(index) + ']'
    person["name"]["instanceName"] = person_list_name + '[' + str(index) + '].name'
    document.pop(person_list_name)

    document[person_list_name] = dict()
    document[person_list_name]["elements"] = list()
    document[person_list_name]["elements"].append(person)
    document[person_list_name]["_class"] = "docassemble.base.core.DAList"
    document[person_list_name]["instanceName"] = person_list_name
    document["valid_" + person_list_name + "_table"] = "continue"


def _create_address_obj(document, person_list_name, index):
    document[person_list_name]["elements"][index]['address']["instanceName"] = person_list_name + '[' + str(index) + '].address'
    document[person_list_name]["elements"][index]['address']["_class"] = "docassemble.base.util.Address"
    document[person_list_name]["auto_gather"] = False
    document[person_list_name]["gathered"] = True


def _create_secret(base_url, api_key, username, user_password):
    try:
        dac = DocassembleClient(base_url, api_key)
        logger.info(
            "Dados do servidor de entrevistas: {base_url} - {api_key}".format(
                base_url=base_url, api_key=api_key
            )
        )
    except NewConnectionError as e:
        message = "Não foi possível estabelecer conexão com o servidor de geração de documentos. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise DocassembleAPIException(message)
    else:
        try:
            response_json, status_code = dac.secret_read(username, user_password)
            secret = response_json
            logger.info(
                "Secret obtido do servidor de geração de documentos: {secret}".format(
                    secret=secret
                )
            )
        except ConnectionError as e:
            message = "Não foi possível obter o secret do servidor de geração de documentos. | {e}".format(
                e=str(e)
            )
            logger.error(message)
            raise DocassembleAPIException(message)
        else:
            if status_code != 200:
                error = "Erro ao gerar o secret | Status Code: {status_code} | Response: {response}".format(
                    status_code=status_code, response=response_json
                )
                logger.error(error)
                raise DocassembleAPIException(error)
            else:
                return secret
