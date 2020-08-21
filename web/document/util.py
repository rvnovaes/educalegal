import logging
import uuid
from enum import Enum
from datetime import datetime

from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError
from util.docassemble_client import DocassembleClient, DocassembleAPIException

from .models import DocumentType

logger = logging.getLogger(__name__)


def custom_class_name(interview_custom_file_name):
    prefix = datetime.today().strftime("%Y%m%d_%H%M%S")
    return prefix + "_" + interview_custom_file_name


def create_secret(base_url, api_key, username, user_password):
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


def dict_to_docassemble_objects(documents, interview_type_id):
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

        elif interview_type_id == DocumentType.NOTIFICACAO_EXTRAJUDICIAL.value:
            # tipos de pessoa no contrato de prestacao de servicos
            person_types = ['notifieds']

            for person in person_types:
                # cria hierarquia para endereço da pessoa
                _build_address_dict(document, person)

                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", person, 0)

                # Cria a representacao do objeto Address da pessoa
                _create_address_obj(document, person, 0)

            document["content_document"] = "notificacao-extrajudicial.docx"

        elif interview_type_id == DocumentType.ACORDOS_TRABALHISTAS_INDIVIDUAIS.value:
            # tipos de pessoa no contrato de prestacao de servicos
            person_types = ['workers']

            for person in person_types:
                # cria hierarquia para endereço da pessoa
                _build_address_dict(document, person)

                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", person, 0)

                # Cria a representacao do objeto Address da pessoa
                _create_address_obj(document, person, 0)

            # Cria a representacao da lista de documentos
            _create_documents_obj(document)

            document["content_document"] = "acordos-individuais-trabalhistas-coronavirus.docx"

        # insere campos fixos
        document["reviewed_school_email_answer"] = True

        # remove campos herdados do mongo e que nao existem na entrevista e converte o objeto OB ID do mongo em campo doc_uuid
        mongo_id = str(document.get("id"))
        document.pop('id')
        document["mongo_uuid"] = mongo_id
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


def _create_documents_obj(document):
    doc_names = {'docmp9272020': 'termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.docx',
                 'docmp9362020': 'acordo-individual-reducao-de-jornada-e-reducao-salarial-mp-936-2020.docx',
                 'docdireitoautoral': 'termo-mudanca-de-regime-e-cessao-do-direito-autoral.docx'}

    elements = dict()
    for doc_type in document['documents_list']:
        elements[doc_names[doc_type]] = document["documents_list"][doc_type]

    document.pop("documents_list")
    document["documents_list"] = dict()
    document["documents_list"]['elements'] = elements
    document["documents_list"]["_class"] = "docassemble.base.core.DADict"
    document["documents_list"]["ask_number"] = False
    document["documents_list"]["ask_object_type"] = False
    document["documents_list"]["auto_gather"] = False
    document["documents_list"]["gathered"] = True
    document["documents_list"]["instanceName"] = "documents_list"

    return document


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
