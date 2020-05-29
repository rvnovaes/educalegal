import logging
import requests
import uuid
from urllib3.exceptions import NewConnectionError
import pandas as pd
import numpy as np
import time
from mongoengine import ValidationError

from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View

from tenant.models import Tenant
from school.models import School, SchoolUnit
from interview.models import Interview, InterviewServerConfig
from interview.util import build_interview_full_name
from mongo_util.mongo_util import create_dynamic_document_class, mongo_to_dict

from .forms import BulkInterviewForm
from .models import BulkGeneration
from .docassemble_client import DocassembleClient

logger = logging.getLogger(__name__)


class ValidateCSVFile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = BulkInterviewForm()
        interview = Interview.objects.get(pk=self.kwargs["interview_id"])
        return render(
            request,
            "bulk_interview/bulk_interview_validate_generate.html",
            {"form": form, "interview_id": interview.pk, "csv_valid": False, "validation_error": False},
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

            # salva o arquivo inserido pelo usuario na pasta media
            fs = FileSystemStorage()
            filename = fs.save(source_file.name, source_file)

            # pega caminho do arquivo para ler o csv com pandas
            absolute_file_path = fs.base_location + "/" + filename

            with open(absolute_file_path) as csvfile:
                bulk_data = pd.read_csv(csvfile, sep=";")

            # A zeresima linha representa os tipos dos campos
            # A primeira linha representa se o campo e required (true / false) como string
            # Ambos são usados para criar a classe dinamica
            field_types_dict = bulk_data.loc[0].to_dict()
            required_fields_dict = bulk_data.loc[1].to_dict()

            field_types_set = set(bulk_data.loc[0].to_list())

            # valid_field_types

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
                school_names_set=school_names_set,
                school_units_names_set=school_units_names_set,
            )
            # Cria novo df apenas com os dados, sem as linhas de tipo, required e labels para usuário final
            # Lembre-se que a linha de header do df se mantem
            bulk_data_content = bulk_data.drop(bulk_data.index[range(0, 4)])

            # Substitui os campos de unidade escolar vazios, aos quais o Pandas havia atribuido nan, por ---
            bulk_data_content["unidadeAluno"] = bulk_data_content[
                "unidadeAluno"
            ].replace({np.nan: "---"})

            # Substitui os campos vazios, aos quais o Pandas havia atribuido nan, por None
            bulk_data_content = bulk_data_content.replace({np.nan: None})

            # Se houver registro invalido, esta variavel sera definida como False ao final da funcao.
            # Esta variavel ira modifica a logica de exibicao das telas ao usuario:
            # Se o CSV for valido, i.e., tiver todos os registros validos, sera exibida a tela de envio
            # Se nao, exibe as mesnagens de sucesso e de erro na tela de carregar novamente o CSV
            csv_valid = True

            # Percorre o df resultante, que possui apenas o conteudo e tenta gravar cada uma das linhas
            # no Mongo
            for register_index, row in enumerate(
                bulk_data_content.itertuples(index=False)
            ):
                # Transforma a linha em dicionario
                row_dict = row._asdict()
                # Cria um objeto Documento a partir da classe dinamica
                dynamic_document = DynamicDocumentClass(**row_dict)
                try:
                    dynamic_document.save()
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
                    # Se a operacao for bem sucedida, itera sobre a lista de valores para gerar a
                    # mensagem de sucesso
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
                finally:
                    # Apaga o arquivo csv carregado
                    fs.delete(filename)
                    # Recupera a lista de mensagens criada
                    # Se nao houver nenhuma mensagem de erro, define o csv como válido

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
                    school_names_set=list(school_names_set),
                    school_units_names_set=list(school_units_names_set),
                )
                bulk_generation.save()
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
                # Apaga a colecao do banco
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
    DynamicDocumentClass = create_dynamic_document_class(
        bulk_generation.mongo_db_collection_name,
        bulk_generation.field_types_dict,
        bulk_generation.required_fields_dict,
        school_names_set=list(bulk_generation.school_names_set),
        school_units_names_set=list(bulk_generation.school_units_names_set),
    )

    documents_collection = DynamicDocumentClass.objects
    documents_collection = list(documents_collection)
    logger.info(
        "Recuperados {n} documento(s) do Mongo".format(n=len(documents_collection))
    )

    interview_variables_list = _dict_from_documents(documents_collection, interview.document_type.pk)

    # Se houver geracao com erro, esta variavel sera definida como False ao final da funcao.
    # Esta variavel ira modifica a logica de exibicao das telas ao usuario
    all_interviews_generated_success = True

    try:
        # lê configurações do servidor da plataforma de geração de documentos (Docassemble)
        isc = InterviewServerConfig.objects.get(interviews=interview.pk)
        base_url = isc.base_url
        api_key = isc.user_key
        username = isc.username
        user_password = isc.user_password
    except ObjectDoesNotExist:
        message = "Não foi configurado o servidor para esta entrevista!"
        logger.error(message)
        messages.error(request, message)
    else:
        # cria cliente da api do docassemble
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
            messages.error(request, message)
        else:
            # monta nome da entrevista de acordo com especificações do docassemble
            interview_full_name = build_interview_full_name(
                isc.user_id,
                isc.project_name,
                interview.yaml_name,
                "interview_filename",
            )

            logger.info(
                "Nome da entrevista: {interview_full_name} ".format(
                    interview_full_name=interview_full_name
                )
            )

            # passa argumentos da url para a entrevista
            url_args = {
                "tid": request.user.tenant.pk,
                "ut": request.user.auth_token.key,
                "intid": interview.pk,
            }

            try:
                response_json, status_code = dac.secret_read(username, user_password)
                secret = response_json
                logger.info(
                    "Secret obtido do servidor de geração de documentos: {secret}".format(
                        secret=secret
                    )
                )
            except requests.exceptions.ConnectionError as e:
                message = "Não foi possível obter o secret do servidor de geração de documentos. | {e}".format(
                    e=str(e)
                )
                logger.error(message)
                messages.error(request, message)
            else:
                if status_code != 200:
                    error_message = "Erro ao gerar o secret | Status Code: {status_code} | Response: {response}".format(
                        status_code=status_code, response=response_json
                    )
                    logger.error(error_message)
                    messages.error(request, error_message)
                else:
                    # gera uma nova entrevista para a cada dicionário de variáveis de entrevista
                    # na lista de  variáveis de entrevista
                    for i, interview_variables in enumerate(interview_variables_list):
                        # Uma nova sessão deve ser criada para cada entrevista
                        try:
                            (
                                interview_session,
                                response_json,
                                status_code,
                            ) = dac.start_interview(interview_full_name, secret)
                            logger.info(
                                "Sessão da entrevista gerada com sucesso: {interview_session}".format(
                                    interview_session=interview_session
                                )
                            )
                        except requests.exceptions.ConnectionError as e:
                            message = "Não foi possível iniciar nova sessão de entrevista. | {e}".format(
                                e=str(e)
                            )
                            logger.error(message)
                            messages.error(request, message)
                        else:
                            if status_code != 200:
                                error_message = "Erro ao iniciar nova sessão | Status Code: {status_code} | Response: {response}".format(
                                    status_code=status_code, response=response_json
                                )
                                logger.error(error_message)
                                messages.error(request, error_message)
                            else:
                                logger.info(
                                    "Gerando documento {document_number} de {bulk_list_lenght}".format(
                                        document_number=str(i + 1),
                                        bulk_list_lenght=str(
                                            len(interview_variables_list)
                                        ),
                                    )
                                )
                                interview_variables["url_args"] = url_args
                                try:
                                    logger.info(
                                        "Tentando gerar entrevista {interview_full_name} com os dados {interview_variables}".format(
                                            interview_full_name=interview_full_name,
                                            interview_variables=interview_variables,
                                        )
                                    )

                                    response, status_code = dac.interview_set_variables(
                                        secret,
                                        interview_full_name,
                                        interview_variables,
                                        interview_session,
                                    )
                                except Exception as e:
                                    error_message = str(e)
                                    logger.error(error_message)
                                    messages.error(request, error_message)
                                else:
                                    if status_code != 200:
                                        error_message = "Erro ao gerar entrevista | Status Code: {status_code} | Response: {response}".format(
                                            status_code=status_code,
                                            response=str(response.text),
                                        )
                                        logger.error(error_message)
                                        messages.error(request, error_message)
                                    else:
                                        # Dispara a action de envio para assinatura eletronica
                                        logger.info(
                                            "Enviando entrevista para assinatura eletronica"
                                        )
                                        # TODO colocar opcao na interface do usuario para escolher se deseja mandar para esignature em lote
                                        if interview_variables["submit_to_esignature"]:
                                            status_code = dac.interview_run_action(
                                                secret,
                                                interview_full_name,
                                                interview_session,
                                                "submit_to_esignature",
                                                None,
                                            )
                                            logger.info(status_code)
                                        message = "Status Code: {status_code} | Response: {response}".format(
                                            status_code=status_code,
                                            response=str(response),
                                        )
                                        logger.info(message)
                                        messages.success(request, message)

    storage = get_messages(request)
    for message in storage:
        if message.level_tag == "error":
            all_interviews_generated_success = False
            break

    return render(
        request,
        "bulk_interview/bulk_interview_generation_result.html",
        {"all_interviews_generated_success": all_interviews_generated_success},
    )


def _dict_from_documents(documents_collection, interview_type_id):

    interview_variables_list = list()

    if interview_type_id == 1:

        for i, document in enumerate(documents_collection):
            logger.info(
                "Gerando lista de variáveis para o objeto {object_id}".format(
                    object_id=str(document.id)
                )
            )

            document = mongo_to_dict(document, [])
            document["submit_to_esignature"] = "False"

            interview_variables_list.append(document)

        logger.info(
            "Criada lista variáveis de documentos a serem gerados em lote com {size} documentos.".format(
                size=len(interview_variables_list)
            )
        )

    if interview_type_id == 2:

        for i, document in enumerate(documents_collection):
            logger.info(
                "Gerando lista de variáveis para o objeto {object_id}".format(
                    object_id=str(document.id)
                )
            )

            document = mongo_to_dict(document, [])

            contratante = dict()
            contratante_attributes = [
                "nacionalidade",
                "estadocivil",
                "prof",
                "cpf",
                "rg",
                "telefone",
                "wtt",
                "email",
                "cep",
                "rua",
                "numb",
                "complemento",
                "bairro",
                "cidade",
                "estado",
            ]
            for attribute in contratante_attributes:
                # Se não houver o atributo no documento, ele estava em branco na planilha
                try:
                    contratante[attribute] = document[attribute]
                    document.pop(attribute)
                except KeyError:
                    contratante[attribute] = ""
            # Cria a representacao do objeto IndividualName dentro de contratante
            contratante["name"] = dict()
            contratante["name"]["first"] = document["name_first"]
            document.pop("name_first")
            contratante["instanceName"] = "contratantes[0]"
            contratante["_class"] = "docassemble.base.util.Individual"
            contratante["name"]["_class"] = "docassemble.base.util.IndividualName"
            contratante["name"]["uses_parts"] = True
            # TODO alteracao do indice para mais de um contratante ??
            contratante["name"]["instanceName"] = "contratantes[0].name"
            contratante["instanceName"] = "contratantes[0]"
            document["contratantes"] = dict()
            document["contratantes"]["elements"] = list()
            document["contratantes"]["elements"].append(contratante)
            document["contratantes"]["auto_gather"] = "False"
            document["contratantes"]["gathered"] = "True"
            document["contratantes"]["_class"] = "docassemble.base.core.DAList"
            document["contratantes"]["instanceName"] = "contratantes"

            document[
                "content_document"
            ] = "contrato-prestacao-servicos-educacionais.docx"
            document["valid_contratantes_table"] = "continue"
            document["submit_to_esignature"] = "True"

            interview_variables_list.append(document)

        logger.info(
            "Criada lista variáveis de documentos a serem gerados em lote com {size} documentos.".format(
                size=len(interview_variables_list)
            )
        )

    if interview_type_id == 37:

        for i, document in enumerate(documents_collection):
            logger.info(
                "Gerando lista de variáveis para o objeto {object_id}".format(
                    object_id=str(document.id)
                )
            )

            document = mongo_to_dict(document, [])

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
                "state"
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
                document["documents_list"]["elements"]["acordo-individual-reducao-de-jornada-e-reducao-salarial-mp-936-2020.docx"] = True
            else:
                document["documents_list"]["elements"]["acordo-individual-reducao-de-jornada-e-reducao-salarial-mp-936-2020.docx"] = False

            if document["docmp9272020"] == "s":
                document["documents_list"]["elements"][
                    "termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.docx"] = True
            else:
                document["documents_list"]["elements"][
                    "termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.docx"] = False

            if document["docdireitoautoral"] == "s":
                document["documents_list"]["elements"]["termo-mudanca-de-regime-e-cessao-do-direito-autoral.docx"] = True
            else:
                document["documents_list"]["elements"][
                    "termo-mudanca-de-regime-e-cessao-do-direito-autoral.docx"] = False

            document["documents_list"]["gathered"] = True
            document["documents_list"]["instanceName"] = "documents_list"
            # document["documents_list"]["minimum_number"]: null,
            # document["documents_list"]["object_type"]: null,
            # document["documents_list"]["object_type_parameters"]: {}

            document[
                "content_document"
            ] = "acordos-individuais-trabalhistas-coronavirus.docx"
            document["valid_workers_table"] = "continue"
            document["submit_to_esignature"] = "False"

            interview_variables_list.append(document)

        logger.info(
            "Criada lista variáveis de documentos a serem gerados em lote com {size} documentos.".format(
                size=len(interview_variables_list)
            )
        )

    return interview_variables_list
