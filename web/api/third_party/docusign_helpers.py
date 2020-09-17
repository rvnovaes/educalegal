import base64
import dateparser
import logging
import os
import xmltodict

from pathlib import Path

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from api.views_v2 import save_in_ged
from document.models import Document, Envelope, Signer, DocumentStatus, DocumentFileKind
from document.views import save_document_data
from interview.models import Interview
from tenant.models import Tenant, ESignatureAppProvider


logger = logging.getLogger(__name__)


envelope_statuses = {
    "sent": {"docusign": "enviado", "el": DocumentStatus.ENVIADO_ASS_ELET.value},
    "delivered": {"docusign": "entregue", "el": DocumentStatus.ENVIADO_ASS_ELET.value},
    "completed": {"docusign": "finalizado", "el": DocumentStatus.ASSINADO.value},
    "declined": {"docusign": "recusado", "el": DocumentStatus.RECUSADO_INVALIDO.value},
    "voided": {"docusign": "inválido", "el": DocumentStatus.RECUSADO_INVALIDO.value},
}

recipient_statuses_dict = {
    "created": "criado",
    "sent": "enviado",
    "delivered": "entregue",
    "signed": "assinado",
    "declined": "recusado",
    "completed": "finalizado",
    "faxpending": "anexo de fax pendente",
    "autoresponded": "respondido automaticamente",
}

recipient_types_dict = {
    "agent": "agente",
    "carboncopy": "em cópia",
    "certifieddelivery": "entrega certificada",
    "editor": "editor",
    "inpersonsigner": "assinatura presencial",
    "intermediary": "intermediário",
    "seal": "selo",
    "signer": "signatário",
    "witness": "testemunha",
}


def docusign_xml_parser(data):
    envelope_data = dict()
    xml = xmltodict.parse(data)["DocuSignEnvelopeInformation"]
    envelope_data["envelope_id"] = xml["EnvelopeStatus"]["EnvelopeID"]
    envelope_data["envelope_status"] = xml["EnvelopeStatus"]["Status"]
    envelope_data["envelope_created"] = xml["EnvelopeStatus"]["Created"]
    envelope_data["envelope_sent"] = xml["EnvelopeStatus"]["Sent"]
    envelope_data["envelope_time_generated"] = xml["EnvelopeStatus"]["TimeGenerated"]

    # converte a data do docusign que vem no formato ISO 8601 (2020-04-15T11:20:19.693) para datetime
    envelope_data['envelope_created'] = dateparser.parse(envelope_data['envelope_created'])
    envelope_data['envelope_sent'] = dateparser.parse(envelope_data['envelope_sent'])
    envelope_data['envelope_time_generated'] = dateparser.parse(envelope_data['envelope_time_generated'])

    # copia com .copy() pra criar outro objeto
    envelope_data_translated = envelope_data.copy()

    # converte datetime para formado brasileiro
    envelope_data_translated['envelope_created'] = str(envelope_data['envelope_created'].strftime('%d/%m/%Y %H:%M:%S'))
    envelope_data_translated['envelope_sent'] = str(envelope_data['envelope_sent'].strftime('%d/%m/%Y %H:%M:%S'))
    envelope_data_translated['envelope_time_generated'] = str(envelope_data['envelope_time_generated'].strftime('%d/%m/%Y %H:%M:%S'))

    envelope_data_translated["envelope_status"] = str(envelope_data_translated["envelope_status"]).lower()
    if envelope_data_translated["envelope_status"] in envelope_statuses.keys():
        envelope_data_translated["envelope_status"] = envelope_statuses[envelope_data_translated["envelope_status"]]['docusign']
    else:
        envelope_data_translated["envelope_status"] = DocumentStatus.NAO_ENCONTRADO.value

    recipient_statuses = xml["EnvelopeStatus"]["RecipientStatuses"]["RecipientStatus"]

    # translation of the type and status of the recipient
    for recipient_status in recipient_statuses:
        recipient_status['Type'] = str(recipient_status['Type']).lower()
        if recipient_status['Type'] in recipient_types_dict.keys():
            recipient_status['Type'] = recipient_types_dict[recipient_status['Type']]
        else:
            recipient_status['Type'] = 'não encontrado'
        recipient_status['Status'] = str(recipient_status['Status']).lower()
        if recipient_status['Status'] in recipient_statuses_dict.keys():
            recipient_status['Status'] = recipient_statuses_dict[recipient_status['Status']]
        else:
            recipient_status['Status'] = 'não encontrado'
        # converte a data do docusign que vem no formato ISO 8601 (2020-04-15T11:20:19.693) para datetime
        if 'Sent' in recipient_status.keys():
            recipient_status['data_envio'] = dateparser.parse(recipient_status['Sent'])
        else:
            recipient_status['data_envio'] = None

    return envelope_data, envelope_data_translated, recipient_statuses


def docusign_pdf_files_parser(data):
    pdf_documents = list()
    xml = xmltodict.parse(data)["DocuSignEnvelopeInformation"]
    # Loop through the DocumentPDFs element to create a variable with the name of the document
    for pdf in xml["DocumentPDFs"]["DocumentPDF"]:
        if pdf["DocumentType"] == "CONTENT":
            main_filename_no_extension = str(pdf["Name"].split(".")[0])
            break
        else:
            main_filename_no_extension = "unnamed_document"

    logger.info(
        "Trying to create documents "
        + main_filename_no_extension
        + " on envelope "
        + str(xml["EnvelopeStatus"]["EnvelopeID"])
    )

    # Loop through the DocumentPDFs element, storing each document.
    for pdf in xml["DocumentPDFs"]["DocumentPDF"]:
        if pdf["DocumentType"] == "CONTENT":
            file_kind = DocumentFileKind.PDF_SIGNED.value
            filename = main_filename_no_extension + "_assinado.pdf"
            description = main_filename_no_extension + ".pdf completo."
        elif pdf["DocumentType"] == "SUMMARY":
            file_kind = DocumentFileKind.PDF_CERTIFIED.value
            filename = main_filename_no_extension + "_certificado.pdf"
            description = (
                main_filename_no_extension + ".pdf certificado de assinaturas."
            )
        else:
            filename = pdf["DocumentType"] + "_" + pdf["Name"]
            description = filename
            file_kind = DocumentFileKind.PDF

        pdf_file_data = dict()
        pdf_file_data["file_kind"] = file_kind
        pdf_file_data["filename"] = filename
        pdf_file_data["description"] = description
        pdf_file_data["file"] = base64.b64decode(pdf["PDFBytes"])
        pdf_documents.append(pdf_file_data)

        # with open(full_filename, "wb") as pdf_file:
        #     pdf_file.write(base64.b64decode(pdf["PDFBytes"]))

    return pdf_documents


@require_POST
@csrf_exempt
def docusign_webhook_listener(request):
    logger.debug(request.headers)
    logger.debug(request.content_type)
    data = request.body  # This is the entire incoming POST content in Django
    try:
        logging.info('docusign_1')
        # Parses XML data and returns a dictionary and formated messages
        envelope_data, envelope_data_translated, recipient_statuses = docusign_xml_parser(data)
        # Store the XML file on disk
        # envelope_dir = os.path.join(settings.BASE_DIR, "media/", relative_path)
        # Path(envelope_dir).mkdir(parents=True, exist_ok=True)

        # filename = (
        #     envelope_data["envelope_time_generated"].strftime("%Y%m%d_%H%M%S") + ".xml"
        # )  # substitute _ for : for windows-land
        # filepath = os.path.join(envelope_dir, filename)

        # with open(filepath, "wb") as xml_file:
        #     xml_file.write(data)
    except Exception as e:
        logging.info('docusign_2')
        message = str(e)
        logger.exception(message)
        return HttpResponse(message)

    try:
        logging.info('docusign_3')
        document = Document.objects.get(envelope_number=envelope_data["envelope_id"])
    except Document.DoesNotExist:
        logging.info('docusign_4')
        message = 'O documento do envelope {envelope_number} não existe.'.format(
            envelope_number=envelope_data["envelope_id"])
        logger.debug(message)
        return HttpResponse(message)
    except Exception as e:
        logging.info('docusign_5')
        message = str(e)
        logger.exception(message)
        logging.info(message)
        return HttpResponse(message)
    else:
        logging.info('docusign_6')
        # quando envia pelo localhost o webhook do docusign vai voltar a resposta para o test, por isso, não irá
        # encontrar o documento no banco
        envelope_status = str(envelope_data["envelope_status"]).lower()

        # variável para salvar o nome dos pdfs no signer
        pdf_filenames = ''

        tenant = Tenant.objects.get(pk=document.tenant.pk)
        # If the envelope is completed, pull out the PDFs from the notification XML an save on disk and send to GED
        if envelope_status == "completed":
            try:
                logging.info('docusign_7')
                (envelope_data["pdf_documents"]) = docusign_pdf_files_parser(data)

                relative_path = 'docs/' + tenant.name + '/' + document.name[:15] + '/'
                has_ged = tenant.has_ged()
                if has_ged:
                    logging.info('docusign_8')
                    # Get document related interview data to post to GED
                    interview = Interview.objects.get(pk=document.interview.pk)
                    document_description = interview.description if interview.description else ''

                    post_data = {
                        "description": document_description,
                        "document_type": interview.document_type.pk,
                        "language": interview.language,
                    }

                    pdf_filenames = list()
                    for pdf in envelope_data["pdf_documents"]:
                        try:
                            logging.info('docusign_*')
                            post_data["label"] = pdf["filename"]
                            status_code, ged_data, ged_id = save_in_ged(post_data, None, pdf["file"], document.tenant)
                        except Exception as e:
                            logging.info('docusign_10')
                            message = str(e)
                            logging.exception(message)
                            return HttpResponse(message)
                        else:
                            logging.info('docusign_11')
                            logger.debug("Posting document to GED: " + pdf["filename"])
                            pdf_filenames.append(pdf["filename"])

                            if status_code == 201:
                                logging.info('docusign_12')
                                # salva o documento baixado no EL como documento relacionado. copia do pai algumas
                                # propriedades
                                related_document = Document(
                                    name=pdf["filename"],
                                    description=document.description,
                                    interview=document.interview,
                                    school=document.school,
                                    tenant=document.tenant,
                                    bulk_generation=document.bulk_generation,
                                    file_kind=pdf["file_kind"],
                                )
                                save_document_data(related_document, None, pdf["file"], has_ged, ged_data,
                                                   relative_path, document)
                            else:
                                logging.info('docusign_13')
                                message = 'Não foi possível salvar o documento no GED. {} - {}'.format(
                                    str(status_code), ged_data)
                                logging.error(message)
                                return HttpResponse(message)

                    # separa os documentos com ENTER
                    pdf_filenames = chr(10).join(pdf_filenames)
                else:
                    for pdf in envelope_data["pdf_documents"]:
                        logging.info('docusign_14')
                        # salva o documento baixado no EL como documento relacionado. copia do pai algumas
                        # propriedades
                        related_document = Document(
                            name=pdf["filename"],
                            description=document.description,
                            interview=document.interview,
                            school=document.school,
                            tenant=document.tenant,
                            bulk_generation=document.bulk_generation,
                            file_kind=pdf["file_kind"],
                        )
                        save_document_data(related_document, None, pdf["file"], relative_path, has_ged, None, document)
                        logging.info('docusign_15')
            except Exception as e:
                logging.info('docusign_16')
                message = str(e)
                logger.exception(message)
                logging.info(message)
                return HttpResponse(message)

        if envelope_status in envelope_statuses.keys():
            document.status = envelope_statuses[envelope_status]['el']
        else:
            document.status = DocumentStatus.NAO_ENCONTRADO.value

        # atualiza o status do documento
        document.save(update_fields=['status'])

        # se o envelope já existe atualiza o status, caso contrário, cria o envelope
        try:
            logging.info('docusign_17')
            envelope = Envelope.objects.get(identifier=envelope_data["envelope_id"])
        except Envelope.DoesNotExist:
            logging.info('docusign_18')
            envelope = Envelope(
                identifier=envelope_data['envelope_id'],
                status=envelope_data_translated['envelope_status'],
                envelope_created_date=envelope_data['envelope_created'],
                sent_date=envelope_data['envelope_sent'],
                status_update_date=envelope_data['envelope_time_generated'],
                signing_provider=ESignatureAppProvider.DOCUSIGN.value,
                tenant=tenant,
            )
            envelope.save()

            # vincula o envelope criado ao documento
            document.envelope = envelope
            document.envelope_number = envelope.identifier
            document.save(update_fields=['envelope', 'envelope_number'])
        else:
            logging.info('docusign_19')
            envelope.status = envelope_data_translated['envelope_status']
            envelope.status_update_date = envelope_data['envelope_time_generated']
            envelope.save(update_fields=['status', 'status_update_date'])

        for recipient_status in recipient_statuses:
            try:
                logging.info('docusign_20')
                # se já tem o status para o email e para o documento, não salva outro igual
                # só cria outro se o status do recipient mudou
                signer = Signer.objects.get(
                    document=document,
                    email=recipient_status['Email'],
                    status=recipient_status['Status'])
            except Signer.DoesNotExist:
                logging.info('docusign_21')
                try:
                    signer = Signer(
                        name=recipient_status['UserName'],
                        email=recipient_status['Email'],
                        status=recipient_status['Status'],
                        sent_date=recipient_status['data_envio'],
                        type=recipient_status['Type'],
                        pdf_filenames=pdf_filenames,
                        document=document,
                        tenant=tenant,
                    )

                    signer.save()
                except Exception as e:
                    logging.info('docusign_22')
                    message = 'Não foi possível salvar o Signer: ' + str(e)
                    logging.info(message)
                    logger.exception(message)

    logging.info('docusign_23')
    return HttpResponse("Success!")
