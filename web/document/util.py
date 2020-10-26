import io
import json
import logging
import requests

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

from api.third_party.clicksign_client import ClickSignClient
from api.third_party.docusign_client import DocuSignClient, make_document_base64
from api.third_party.sendgrid_client import send_email as sendgrid_send_email
from document.models import Document, DocumentStatus
from tenant.models import ESignatureAppProvider, ESignatureAppSignerKey

from .models import BulkDocumentKind

logger = logging.getLogger(__name__)


def custom_class_name(interview_custom_file_name):
    prefix = datetime.today().strftime("%Y%m%d_%H%M%S")
    return prefix + "_" + interview_custom_file_name


def dict_to_docassemble_objects(documents, interview_type_id):
    interview_variables_list = list()

    for document in documents:
        logger.info(
            "Gerando lista de variáveis para o objeto {object_id}".format(
                object_id=str(document['id'])
            )
        )

        if interview_type_id == BulkDocumentKind.PRESTACAO_SERVICOS_ESCOLARES.value:
            # tipos de pessoa no contrato de prestacao de servicos
            parents = ['students', 'contractors']

            for parent in parents:
                # cria hierarquia para endereço da pessoa
                _build_address_dict(document, parent)

                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", parent)

                # Cria a representacao do objeto Address da pessoa
                _create_address_obj(document, parent)

                _create_da_list_properties(document, parent)

            # para objetos do tipo Thing
            parents = ['input_installments_data', 'other_installments_data']

            for parent in parents:
                # Cria a representacao do objeto Thing
                _create_thing_obj(document, parent)

                _create_da_list_properties(document, parent)

            # para pessoas que nao tem endereco
            parents = ['witnesses']

            for parent in parents:
                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", parent)

                _create_da_list_properties(document, parent)

            document["valid_input_installments_data_table"] = "continue"
            document["valid_other_installments_data_table"] = "continue"
            document["content_document"] = "contrato-prestacao-servicos-educacionais.docx"

        elif interview_type_id == BulkDocumentKind.NOTIFICACAO_EXTRAJUDICIAL.value:
            # tipos de pessoa no contrato de prestacao de servicos
            parents = ['notifieds']

            for parent in parents:
                # cria hierarquia para endereço da pessoa
                _build_address_dict(document, parent)

                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", parent)

                # Cria a representacao do objeto Address da pessoa
                _create_address_obj(document, parent)

                _create_da_list_properties(document, parent)

            document["content_document"] = "notificacao-extrajudicial.docx"

        elif interview_type_id == BulkDocumentKind.ACORDOS_TRABALHISTAS_INDIVIDUAIS.value:
            # tipos de pessoa no contrato de prestacao de servicos
            parents = ['workers']

            for parent in parents:
                # cria hierarquia para endereço da pessoa
                _build_address_dict(document, parent)

                # Cria a representacao do objeto Individual da pessoa
                _create_person_obj(document, "f", parent)

                # Cria a representacao do objeto Address da pessoa
                _create_address_obj(document, parent)

                _create_da_list_properties(document, parent)

            # Cria a representacao da lista de documentos
            _create_documents_obj(document)

            document["content_document"] = "acordos-individuais-trabalhistas-coronavirus.docx"

        # insere campos fixos
        document["reviewed_school_email_answer"] = True

        # remove campos herdados do mongo e que nao existem na entrevista e converte o objeto OB ID do mongo
        # em campo doc_uuid
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


def _build_name_dict(document, parent, empty=False):
    for element in document[parent]['elements']:
        element["name"] = dict()
        if empty:
            element["name"]["text"] = None
        else:
            element["name"]["text"] = element["name_text"]
            element.pop("name_text")

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

    for element in document[parent]['elements']:
        for attribute in address_attributes:
            address[attribute] = element[attribute]
            element.pop(attribute)

        # adiciona o dicionario endereco na lista de elementos
        element["address"] = address


def _create_documents_obj(document):
    doc_names = {'docmp9272020': 'termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.docx',
                 'docmp9362020': 'acordo-individual-reducao-de-jornada-e-reducao-salarial-mp-936-2020.docx',
                 'docdireitoautoral': 'termo-mudanca-de-regime-e-cessao-do-direito-autoral.docx'}

    elements = dict()
    for doc_type in document['documents_list']['elements']:
        elements[doc_names[doc_type]] = document["documents_list"]['elements'][doc_type]

    document.pop("documents_list")
    document["documents_list"] = dict()
    document["documents_list"]['elements'] = elements
    document["documents_list"]["_class"] = "docassemble.base.core.DADict"
    document["documents_list"]["ask_number"] = False
    document["documents_list"]["ask_object_type"] = False
    document["documents_list"]["auto_gather"] = False
    document["documents_list"]["gathered"] = True
    document["documents_list"]["instanceName"] = "documents_list"


def _create_person_obj(document, person_type, parent):
    """ Cria a representação da pessoa como objeto do Docassemble
        document
        person_type: f  - física
                     j  - jurídica
                     fj - ambos
        parent: students, contractors, witnesses, etc.
    """
    # cria hierarquia para name do person_list_name
    _build_name_dict(document, parent)

    for index, element in enumerate(document[parent]['elements']):
        if person_type == 'fj':
            element["_class"] = "docassemble.base.util.Person"
            element["name"]["_class"] = "docassemble.base.util.Name"
        elif person_type == 'f':
            element["_class"] = "docassemble.base.util.Individual"
            element["name"]["_class"] = "docassemble.base.util.IndividualName"
            element["name"]["uses_parts"] = True
        else:
            element["_class"] = "docassemble.base.util.Organization"
            element["name"]["_class"] = "docassemble.base.util.Name"

        element["instanceName"] = parent + '[' + str(index) + ']'
        element["name"]["instanceName"] = parent + '[' + str(index) + '].name'


def _create_address_obj(document, parent):
    for index, element in enumerate(document[parent]['elements']):
        element['address']["instanceName"] = parent + '[' + str(index) + '].address'
        element['address']["_class"] = "docassemble.base.util.Address"


def _create_da_list_properties(document, parent):
    if parent not in document:
        return

    document[parent]["_class"] = "docassemble.base.core.DAList"
    document[parent]["instanceName"] = parent
    document[parent]["auto_gather"] = False
    document[parent]["gathered"] = True
    document["valid_" + parent + "_table"] = "continue"


def _create_thing_obj(document, parent):
    if parent not in document:
        return

    # cria hierarquia para name do person_list_name
    _build_name_dict(document, parent, True)

    for index, element in enumerate(document[parent]['elements']):
        element["_class"] = "docassemble.base.util.Thing"
        element["name"]["_class"] = "docassemble.base.util.Name"

        element["instanceName"] = parent + '[' + str(index) + ']'
        element["name"]["instanceName"] = parent + '[' + str(index) + '].name'


@login_required
def redirect_send_email(request, doc_uuid):
    status_code, message = send_email(doc_uuid)

    if status_code == 202:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('document:document-detail', doc_uuid)


def send_email(doc_uuid):
    try:
        document = Document.objects.get(doc_uuid=doc_uuid)
    except Document.DoesNotExist:
        message = 'Não foi encontrado o documento com o uuid = {}'.format(doc_uuid)
        logger.error(message)
        return 404, message
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)
        return 500, message
    else:
        if document.recipients:
            to_emails = document.recipients

            if isinstance(to_emails, str):
                # converte string para dict
                to_emails = json.loads(to_emails)

            school_name = document.school.name if document.school.name else document.school.legal_name
            interview_name = document.interview.name if document.interview.name else ''
            subject = "IMPORTANTE: " + school_name + " | " + interview_name
            category = document.name
            if category.endswith('.pdf'):
                category = category[:-4]
            html_content = "<h3>" + document.interview.name + "</h3><p>Leia com atenção o documento em anexo.</p>"
            file_name = document.name

            file = None

            if document.cloud_file:
                response = requests.get(document.cloud_file.url)
                file = io.BytesIO(response.content)
            else:
                if document.tenant.plan.use_ged and document.ged_link:
                    response = requests.get(document.ged_link)
                    file = io.BytesIO(response.content)

            try:
                status_code, response_json = sendgrid_send_email(
                    to_emails, subject, html_content, category, file_name, file)
            except Exception as e:
                status_code = 500
                message = ''
                if hasattr(e, 'to_dict'):
                    for error in e.to_dict['errors']:
                        message += error['message'] + ' | '
                        status_code = e.status_code
                else:
                    message = str(type(e).__name__) + " : " + str(e)

                return status_code, message
            else:
                if status_code == 202:
                    document.send_email = True
                    document.status = DocumentStatus.ENVIADO_EMAIL.value
                    document.save(update_fields=['send_email', 'status'])

                    to_recipients = ''
                    for recipient in to_emails:
                        to_recipients += '<br/>' + recipient['name'] + ' - ' + recipient['email']

                    message = mark_safe('O e-mail foi enviado com sucesso para os destinatários:{}'.format(
                        to_recipients))
                else:
                    message = response_json
                    logger.error(message)
        else:
            return 404, 'Não foram encontrados destinatários no documento ID = {}.'.format(document.id)

    return status_code, message


@login_required
def redirect_send_to_esignature(request, doc_uuid):
    status_code, message = send_to_esignature(doc_uuid)

    # o docusign retorna 201 e o clicksign retorna 202
    if status_code == 202 or status_code == 201:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect('document:document-detail', doc_uuid)


def send_to_esignature(doc_uuid):
    try:
        document = Document.objects.get(doc_uuid=doc_uuid)
    except Document.DoesNotExist:
        message = 'Não foi encontrado o documento com o uuid = {}'.format(doc_uuid)
        logger.error(message)
        return 404, message
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logger.error(message)
        return 500, message
    else:
        status_code = 500
        message = ''
        if document.recipients:
            if isinstance(document.recipients, str):
                # converte string para dict
                document.recipients = json.loads(document.recipients)

            if document.tenant.plan.use_esignature:
                if not document.tenant.esignature_app:
                    message = 'Entre em contato com a nossa equipe para configurar o envio de assinatura eletrônica ' \
                              'pela plataforma.'
                    status_code = 400
                    return status_code, message
            else:
                message = 'Plano contratado: {}. Entre em contato com a nossa equipe para adquirir um plano com ' \
                          'assinatura eletrônica.'.format(document.tenant.plan.name)
                status_code = 400
                return status_code, message

            esignature_app = document.tenant.esignature_app

            if not document.cloud_file:
                message = 'Não foi encontrado o caminho do arquivo para envio para a assinatura eletrônica. ' \
                          'Entre em contato com o suporte.'
                status_code = 400
                return status_code, message

            response = requests.get(document.cloud_file.url)
            file = io.BytesIO(response.content)

            documents = [
                {
                    'name': document.name,
                    'fileExtension': 'pdf',
                    'documentBase64': make_document_base64(file)
                }
            ]

            if esignature_app.provider == ESignatureAppProvider.DOCUSIGN.name:
                dsc = DocuSignClient(esignature_app.client_id, esignature_app.impersonated_user_guid,
                                     esignature_app.test_mode, esignature_app.private_key)

                try:
                    status_code, response_json = dsc.send_to_docusign(
                        document.recipients, documents, email_subject="Documento para sua assinatura")
                except Exception as e:
                    message = str(type(e).__name__) + " : " + str(e)
                    logger.error(message)
                    return 400, message
                else:
                    if status_code == 201:
                        document.submit_to_esignature = True
                        document.status = DocumentStatus.ENVIADO_ASS_ELET.value
                        document.envelope_number = response_json['envelopeId']
                        document.save(update_fields=['submit_to_esignature', 'status', 'envelope_number'])

                        to_recipients = ''
                        for recipient in document.recipients:
                            to_recipients += '<br/>' + recipient['name'] + ' - ' + recipient['email']

                        message = mark_safe('Documento enviado para a assinatura eletrônica com sucesso para os '
                                            'destinatários:{}'.format(to_recipients))
                    else:
                        return status_code, response_json

            elif esignature_app.provider == ESignatureAppProvider.CLICKSIGN.name:
                csc = ClickSignClient(esignature_app.private_key, esignature_app.test_mode)

                documents[0]["tenant"] = dict()
                documents[0]["school"] = dict()
                documents[0]["tenant"]["esignature_folder"] = document.tenant.esignature_folder
                documents[0]["school"]["esignature_folder"] = document.school.esignature_folder

                # faz o upload do documento no clicksign
                status_code, response_json, envelope_number = csc.upload_document(documents[0])

                if status_code == 201:
                    # verifica se o signer ja foi enviado para a clicksign
                    success, recipients_sign = get_signer_key_by_email(document.recipients, document.tenant)
                    if not success:
                        message = 'Não foi possível localizar o signatário por e-mail.'
                        status_code = 400
                        return status_code, message

                    # cria os destinatarios
                    status_code, reason = csc.add_signer(recipients_sign)
                    if status_code != 201:
                        return status_code, reason

                    # adiciona signer key no educa legal
                    if not post_signer_key(recipients_sign, esignature_app, document.tenant):
                        message = 'Não foi possível salvar o signatário no sistema.'
                        status_code = 400
                        return status_code, message

                    # adiciona os signatarios ao documento e envia por email para o primeiro signatario
                    # o envelope_id eh a key do documento no clicksign
                    status_code, response_json = csc.send_to_signers(envelope_number, recipients_sign)

                    if status_code == 202:
                        # atualiza dados do envelope no documento do EL
                        document.status = DocumentStatus.ENVIADO_ASS_ELET.value
                        document.envelope_number = envelope_number
                        document.submit_to_esignature = True
                        document.save(update_fields=['status', 'envelope_number', 'submit_to_esignature'])

                        to_recipients = ''
                        for recipient in document.recipients:
                            to_recipients += '<br/>' + recipient['name'] + ' - ' + recipient['email']

                        message = mark_safe('Documento enviado para a assinatura eletrônica com sucesso para os '
                                            'destinatários:{}'.format(to_recipients))
                    else:
                        return status_code, response_json
                else:
                    return status_code, response_json

        else:
            return 404, 'Não foram encontrados destinatários no documento ID = {}.'.format(document.id)

    return status_code, message


def get_signer_key_by_email(recipients, tenant):
    # separa somente os destinatarios que assinam o documento
    recipients_sign = list()

    if isinstance(recipients, str):
        # converte string para dict
        recipients = json.loads(recipients)

    for recipient in recipients:
        if recipient['group'] == 'signers':
            recipient['group'] = 'sign'
            # a clicksign nao aceita barras no nome
            recipient['name'] = recipient['name'].replace('/', '')
            recipient['name'] = recipient['name'].replace('\\', '')
            recipients_sign.append(recipient)

    for recipient in recipients_sign:
        try:
            e_signature_app_signer_key = ESignatureAppSignerKey.objects.get(
                tenant=tenant, esignature_app=tenant.esignature_app, email=recipient['email'], name=recipient['name'])
        except ESignatureAppSignerKey.DoesNotExist:
            recipient['key'] = ''
            recipient['new_signer'] = True
            recipient['status_code'] = 404
        except Exception as e:
            message = 'Erro ao obter a chave do signatário. ' + str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return False, None
        else:
            recipient['key'] = e_signature_app_signer_key.key
            recipient['new_signer'] = False
            recipient['status_code'] = 200

    return True, recipients_sign


def post_signer_key(recipients, esignature_app, tenant):
    for recipient in recipients:
        if recipient['new_signer'] and recipient['status_code'] == 201:
            e_signature_app_signer_key = ESignatureAppSignerKey(
                email=recipient['email'],
                name=recipient['name'],
                key=recipient['key'],
                esignature_app=esignature_app,
                tenant=tenant,
            )
            try:
                e_signature_app_signer_key.save()
            except IntegrityError:
                pass
            except Exception as e:
                message = str(type(e).__name__) + " : " + str(e)
                logger.error(message)
                return False

    return True
