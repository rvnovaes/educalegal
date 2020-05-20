import logging
import requests
import uuid
from urllib3.exceptions import NewConnectionError
import pandas as pd
import numpy as np

from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import View
from mongoengine import ValidationError


from .docassemble_client import DocassembleClient
from interview.models import Interview, InterviewServerConfig
from interview.util import build_interview_full_name
from mongo_util.mongo_util import create_dynamic_document_class, mongo_to_dict

from .forms import BulkInterviewForm
from .models import BulkGeneration

logger = logging.getLogger(__name__)


class ValidadeCSVFile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = BulkInterviewForm()
        interview = Interview.objects.get(pk=self.kwargs["interview_id"])
        return render(
            request,
            "bulk_interview/bulk_interview_validate_generate.html",
            {"form": form, "interview_id": interview.pk},
        )

    def post(self, request, *args, **kwargs):
        form = BulkInterviewForm(request.POST, request.FILES)
        interview = Interview.objects.get(pk=self.kwargs["interview_id"])
        if form.is_valid():
            source_file = request.FILES["source_file"]
            logger.debug("Carregado o arquivo: " + source_file.name)

            # salva o arquivo inserido pelo usuario na pasta media
            fs = FileSystemStorage()
            filename = fs.save(source_file.name, source_file)

            # pega caminho do arquivo para ler o csv com pandas
            absolute_file_path = fs.base_location + "/" + filename

            with open(absolute_file_path) as csvfile:
                bulk_data = pd.read_csv(csvfile)

            # A zeresima linha representa os tipos dos campos
            # A primeira linha representa se o campo e required (true / false) como string
            # Ambos são usados para criar a classe dinamica
            field_types_dict = bulk_data.loc[0].to_dict()
            required_fields_dict = bulk_data.loc[1].to_dict()

            # O nome da collection deve ser unico no Mongo, pq cada collection representa uma acao
            # de importação. Precisaremos do nome da collection depois para recuperá-la do Mongo]
            # uuid4 gera um UUID aleatorio
            dynamic_document_class_name = (
                interview.custom_file_name + "_bulk_" + str(uuid.uuid4())
            )
            # Cria a classe do tipo Document (mongoengine) dinamicamente
            DynamicDocumentClass = create_dynamic_document_class(
                dynamic_document_class_name, field_types_dict, required_fields_dict,
            )
            # Estabelece, por padrao que o CSV tem registros invalidos. Se nao houve nenhum registro
            # invalido, esta variavel sera definida como True.
            # Esta variavel ira modifica a logica de exibicao das telas ao usuario:
            # Se o CSV for valido, i.e., tiver todos os registros validos, sera exibida a tela de envio
            # Se nao, exibe as mesnagens de sucesso e de erro na tela de carregar novamente o CSV
            csv_valid = False

            # Cria novo df apenas com os dados, sem as linhas de tipo, required e labels para usuário final
            # Lembre-se que a linha de header do df se mantem
            bulk_data_content = bulk_data.drop(bulk_data.index[range(0, 4)])

            # Substitui os campos vazios, aos quais o Pandas havia atribuido nan, por None
            bulk_data_content = bulk_data_content.replace({np.nan: None})

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
                    message = "Registro validado com sucesso " + str(register_index + 1)
                    for value_index, value in enumerate(row_values):
                        message += " | " + str(row_values[value_index])
                    logger.debug(message)
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
                    logger.debug(message)
                    messages.error(request, message)
                finally:
                    # Apaga o arquivo csv carregado
                    fs.delete(filename)
                    # Recupera a lista de mensagens criara
                    # Se nao houver nenhuma mensagem de erro, define o csv como válido
                    storage = get_messages(request)
                    for message in storage:
                        if not message.level_tag == "error":
                            csv_valid = True
            if csv_valid:
                bulk_generation = BulkGeneration(
                    tenant=request.user.tenant,
                    interview=interview,
                    mongo_db_collection_name=dynamic_document_class_name,
                    field_types_dict=field_types_dict,
                    required_fields_dict=required_fields_dict
                )
                bulk_generation.save()

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
                        "csv_valid": csv_valid,
                    },
                )


@login_required
def generate_bulk_documents(request, bulk_generation_id):
    bulk_generation = BulkGeneration.objects.get(pk=bulk_generation_id)
    interview = Interview.objects.get(pk=bulk_generation.interview.pk)
    DynamicDocumentClass = create_dynamic_document_class(
        bulk_generation.mongo_db_collection_name, bulk_generation.field_types_dict, bulk_generation.required_fields_dict,
    )
    documents_collection = DynamicDocumentClass.objects

    # collection_name = bulk_generation.mongo_db_collection_name
    # db = pymongo_client.educalegal
    # documents_collection = db[collection_name]
    interview_variables_list = _dict_from_documents(
        documents_collection, interview.pk
    )

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

            # passa argumentos da url para a entrevista
            url_args = {
                "tid": request.user.tenant.pk,
                "ut": request.user.auth_token.key,
                "intid": interview.pk,
            }

            try:
                secret = dac.secret_read(username, user_password)
            except requests.exceptions.ConnectionError as e:
                message = "Não foi possível obter o secret do servidor de geração de documentos. | {e}".format(
                    e=str(e)
                )
                logger.debug(message)
                messages.error(request, message)
            else:
                # gera uma nova entrevista para a cada dicionário de variáveis de entrevista na lista de
                # variáveis de entrevista
                for i, interview_variables in enumerate(
                    interview_variables_list
                ):
                    # Uma nova sessão deve ser criada para cada entrevista
                    try:
                        interview_session = dac.start_interview(
                            interview_full_name, secret
                        )
                    except requests.exceptions.ConnectionError as e:
                        message = "Não foi possível iniciar nova sessão de entrevista. | {e}".format(
                            e=str(e)
                        )
                        logger.debug(message)
                        messages.error(request, message)
                    else:
                        logger.debug(
                            "Gerando documento {document_number} de {bulk_list_lenght}".format(
                                document_number=str(i + 1),
                                bulk_list_lenght=str(
                                    len(interview_variables_list)
                                ),
                            )
                        )
                        interview_variables["url_args"] = url_args
                        try:
                            logger.debug(
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
                            logger.debug(error_message)
                            messages.error(request, error_message)
                        else:
                            if status_code != 200:
                                error_message = "Status Code: {status_code} | Response: {response}".format(
                                    status_code=status_code, response=response
                                )
                                logger.debug(error_message)
                                messages.error(request, error_message)
                            else:
                                # Dispara a action de envio para assinatura eletronica
                                logger.debug(
                                    "Enviando entrevista para assinatura eletronica"
                                )
                                if interview_variables["submit_to_esignature"]:
                                    status_code = dac.interview_run_action(
                                        secret,
                                        interview_full_name,
                                        interview_session,
                                        "submit_to_esignature",
                                        None,
                                    )
                                    logger.debug(status_code)
                                message = "Status Code: {status_code} | Response: {response}".format(
                                    status_code=status_code, response=response
                                )
                                logger.debug(message)
                                messages.success(request, message)
    return render(
        request,
        "bulk_interview/bulk_interview_generation_result.html",
        {"successful": "successful"},
    )


def _dict_from_documents(documents_collection, interview_type_id):
    interview_variables_list = list()
    if interview_type_id == 2:
        # cursor = documents_collection.find({})
        # Passa os atributos do documento para o contratante
        # e os remove do documento

        for i, document in enumerate(documents_collection):
            logger.debug(
                "Gerando lista de variáveis para o objeto {object_id}".format(object_id=str(document.id))
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

            document["content_document"] = "contrato-prestacao-servicos-educacionais.docx"
            document["valid_contratantes_table"] = "continue"
            document["submit_to_esignature"] = "True"

            interview_variables_list.append(document)

    logger.debug(
        "Criada lista variáveis de documentos a serem gerados em lote com {size} documentos.".format(
            size=len(interview_variables_list)
        )
    )

    return interview_variables_list


@login_required
def bulk_interview(request, interview_id):
    row_errors = []
    if request.method == "POST":
        form = BulkInterviewForm(request.POST, request.FILES)
        if form.is_valid():
            source_file = request.FILES["source_file"]
            logger.debug("Carregado o arquivo: " + source_file.name)

            # salva o arquivo inserido pelo usuario na pasta media
            fs = FileSystemStorage()
            filename = fs.save(source_file.name, source_file)

            # pega caminho do arquivo para ler o csv com pandas
            absolute_file_path = fs.base_location + "/" + filename

            interview = Interview.objects.get(pk=interview_id)
            # gera dicionario de variaveis da entrevista de acordo com o layout da entrevista
            interview_variables_list = _dict_from_csv(
                absolute_file_path, interview.document_type.id
            )

            try:
                # lê configurações do servidor da plataforma de geração de documentos (Docassemble)
                isc = InterviewServerConfig.objects.get(interviews=interview_id)
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

                    # passa argumentos da url para a entrevista
                    url_args = {
                        "tid": request.user.tenant.pk,
                        "ut": request.user.auth_token.key,
                        "intid": interview_id,
                    }

                    try:
                        secret = dac.secret_read(username, user_password)
                    except requests.exceptions.ConnectionError as e:
                        message = "Não foi possível obter o secret do servidor de geração de documentos. | {e}".format(
                            e=str(e)
                        )
                        logger.debug(message)
                        messages.error(request, message)
                    else:
                        # gera uma nova entrevista para a cada dicionário de variáveis de entrevista na lista de variáveis de entrevista
                        for i, interview_variables in enumerate(
                            interview_variables_list
                        ):
                            # Uma nova sessão deve ser criada para cada entrevista
                            try:
                                interview_session = dac.start_interview(
                                    interview_full_name, secret
                                )
                            except requests.exceptions.ConnectionError as e:
                                message = "Não foi possível iniciar nova sessão de entrevista. | {e}".format(
                                    e=str(e)
                                )
                                logger.debug(message)
                                messages.error(request, message)
                            else:
                                logger.debug(
                                    "Gerando documento {document_number} de {bulk_list_lenght}".format(
                                        document_number=str(i + 1),
                                        bulk_list_lenght=str(
                                            len(interview_variables_list)
                                        ),
                                    )
                                )
                                interview_variables["url_args"] = url_args
                                try:
                                    logger.debug(
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
                                    logger.debug(error_message)
                                    messages.error(request, error_message)
                                else:
                                    if status_code != 200:
                                        error_message = "Status Code: {status_code} | Response: {response}".format(
                                            status_code=status_code, response=response
                                        )
                                        logger.debug(error_message)
                                        messages.error(request, error_message)
                                    else:
                                        # Dispara a action de envio para assinatura eletronica
                                        logger.debug(
                                            "Enviando entrevista para assinatura eletronica"
                                        )
                                        if interview_variables["submit_to_esignature"]:
                                            status_code = dac.interview_run_action(
                                                secret,
                                                interview_full_name,
                                                interview_session,
                                                "submit_to_esignature",
                                                None,
                                            )
                                            logger.debug(status_code)
                                        message = "Status Code: {status_code} | Response: {response}".format(
                                            status_code=status_code, response=response
                                        )
                                        logger.debug(message)
                                        messages.success(request, message)

            # apaga o arquivo importado da pasta media
            fs.delete(filename)

    else:
        form = BulkInterviewForm()

    return render(
        request,
        "bulk_interview/bulk_interview.html",
        {"form": form, "interview_id": interview_id, "row_errors": row_errors},
    )


def _dict_from_csv(absolute_file_path, document_type_id):
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html?highlight=orient
    # orient : Series - default is index
    # allowed values are {split, records, index}
    # records - list like [{column -> value}, … , {column -> value}]
    # variables_list = pd.read_csv(filename).to_dict(orient='records')
    if document_type_id == 2:
        interview_variables_list = pd.read_csv(
            absolute_file_path,
            usecols=[
                "selected_school",
                "unidadeAluno",
                "nomeAluno",
                "nacionalidadeAluno",
                "cpfAluno",
                "rgAluno",
                "cepAluno",
                "ruaAluno",
                "numbAluno",
                "compleAluno",
                "bairroAluno",
                "cidadeAluno",
                "estadoAluno",
                "serieAluno",
                "periodoAluno",
                "anoLetivo",
                "valorAnual",
                "desconto",
                "obs",
                "parcelas",
                "primeiraParcela",
                "vencimentoParcelas",
                "signature_local",
                "signature_date",
            ],
            keep_default_na=False,
        )

        interview_variables_list["anoLetivo"] = interview_variables_list[
            "anoLetivo"
        ].astype(int)
        interview_variables_list["valorAnual"] = interview_variables_list[
            "valorAnual"
        ].astype(float)

        interview_variables_list = interview_variables_list.to_dict(orient="records")

        contratantes_list = pd.read_csv(
            absolute_file_path,
            usecols=[
                "name.first",
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
            ],
            keep_default_na=False,
        ).to_dict(orient="records")

        # insere na variables a lista de contratantes
        for i, item in enumerate(contratantes_list):
            interview_variables_list[i][
                "content_document"
            ] = "contrato-prestacao-servicos-educacionais.docx"
            interview_variables_list[i]["valid_contratantes_table"] = "continue"
            interview_variables_list[i]["submit_to_esignature"] = "True"
            # Transforma o nome em objeto do Docassemble
            item["name"] = dict()
            item["name"]["first"] = item["name.first"]
            item["name"]["_class"] = "docassemble.base.util.IndividualName"
            item["name"]["uses_parts"] = True
            # # TODO alteracao do indice para mais de um contratante
            item["name"]["instanceName"] = "contratantes[0].name"  # <-- Isso?
            item["instanceName"] = "contratantes[0]"
            item.pop("name.first")
            item["_class"] = "docassemble.base.util.Individual"
            interview_variables_list[i]["contratantes"] = dict()
            interview_variables_list[i]["contratantes"]["elements"] = list()
            interview_variables_list[i]["contratantes"]["elements"].append(item)
            interview_variables_list[i]["contratantes"]["auto_gather"] = "False"
            interview_variables_list[i]["contratantes"]["gathered"] = "True"
            interview_variables_list[i]["contratantes"][
                "_class"
            ] = "docassemble.base.core.DAList"
            interview_variables_list[i]["contratantes"]["instanceName"] = "contratantes"

        logger.debug(
            "Criada lista variáveis de documentos a serem gerados em lote com {size} documentos.".format(
                size=len(interview_variables_list)
            )
        )

    return interview_variables_list
