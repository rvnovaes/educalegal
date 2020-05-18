import csv
import logging
import requests
import traceback
from urllib3.exceptions import NewConnectionError
import pandas as pd
from mongoengine import ValidationError

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from .docassemble_client import DocassembleClient
from interview.models import Interview, InterviewServerConfig

from mongo_util.mongo_util import create_dynamic_document_class

from .forms import BulkInterviewForm
from .models import BulkGeneration

logger = logging.getLogger(__name__)


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
                user_key = isc.user_key
                username = isc.username
                user_password = isc.user_password
            except ObjectDoesNotExist:
                message = "Não foi configurado o servidor para esta entrevista!"
                logger.error(message)
                messages.error(request, message)
            else:
                # cria cliente da api do docassemble
                try:
                    dac = DocassembleClient(base_url, user_key)
                except NewConnectionError as e:
                    message = str(e)
                    logger.error(message)
                    messages.error(request, message)

                # monta nome da entrevista de acordo com especificações do docassemble
                interview_name = "docassemble.playground{user_id}{project_name}:{interview_name}".format(
                    user_id=isc.user_id,
                    project_name=isc.project_name,
                    interview_name=interview.yaml_name,
                )

                # passa argumentos da url para a entrevista
                url_args = {
                    "tid": request.user.tenant.pk,
                    "ut": request.user.auth_token.key,
                    "intid": interview_id,
                }

                try:
                    secret = dac.secret_read(username, user_password)
                except requests.exceptions.ConnectionError:
                    message = "Não foi possível conectar com o servidor de geração de documentos."
                    logger.debug(message)
                    messages.debug(request, message)
                else:
                    # gera entrevista para a lista de variáveis
                    for row, variable in enumerate(interview_variables_list):
                        logger.debug(
                            "Gerando documento {document_number} de {bulk_list_lenght}".format(
                                document_number=str(row + 1),
                                bulk_list_lenght=str(len(interview_variables_list)),
                            )
                        )
                        variable["url_args"] = url_args
                        try:
                            response, status_code = dac.interview_set_variables(
                                secret, interview_name, variable
                            )
                        except Exception as e:
                            error_message = str(e)
                            logger.debug(error_message)
                            messages.error(request, error_message)
                        else:
                            message = "Entrevistas geradas com sucesso!"
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
        ).to_dict(orient="records")

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
            interview_variables_list[i]["contratantes"] = item
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
