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

from document.models import Document, EnvelopeLog, SignerLog, DocumentStatus
from interview.models import Interview
from tenant.models import Tenant, TenantGedData

from .mayan_helpers import MayanClient


logger = logging.getLogger(__name__)


envelope_statuses = {
    "sent": "enviado",
    "delivered": "entregue",
    "completed": "finalizado",
    "declined": "recusado",
    "voided": "inválido",
}

envelope_vs_document_statuses = {
    "sent": DocumentStatus.ENVIADO_ASS_ELET,
    "delivered": DocumentStatus.ENVIADO_ASS_ELET,
    "completed": DocumentStatus.ASSINADO,
    "declined": DocumentStatus.RECUSADO_INVALIDO,
    "voided": DocumentStatus.RECUSADO_INVALIDO,
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

    logger.info('Envelope_data antes do parse')
    logger.info(envelope_data)

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
        envelope_data_translated["envelope_status"] = envelope_statuses[envelope_data_translated["envelope_status"]]
    else:
        envelope_data_translated["envelope_status"] = DocumentStatus.NAO_ENCONTRADO

    recipient_statuses = xml["EnvelopeStatus"]["RecipientStatuses"]["RecipientStatus"]

    logger.info('recipient_statuses antes do parse')
    logger.info(recipient_statuses)

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


def docusign_pdf_files_saver(data, envelope_dir):
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
            filename = main_filename_no_extension + "_assinado.pdf"
            description = main_filename_no_extension + ".pdf completo."
        elif pdf["DocumentType"] == "SUMMARY":
            filename = main_filename_no_extension + "_certificado.pdf"
            description = (
                main_filename_no_extension + ".pdf certificado de assinaturas."
            )
        else:
            filename = pdf["DocumentType"] + "_" + pdf["Name"]
            description = filename

        full_filename = os.path.join(envelope_dir, filename)
        pdf_file_data = dict()
        pdf_file_data["filename"] = filename
        pdf_file_data["description"] = description
        pdf_file_data["full_filename"] = full_filename
        pdf_documents.append(pdf_file_data)

        with open(full_filename, "wb") as pdf_file:
            pdf_file.write(base64.b64decode(pdf["PDFBytes"]))

    return pdf_documents


@require_POST
@csrf_exempt
def docusign_webhook_listener(request):
    logger.debug(request.headers)
    logger.debug(request.content_type)
    data = request.body  # This is the entire incoming POST content in Django
    try:
        # Parses XML data and returns a dictionary and formated messages
        envelope_data, envelope_data_translated, recipient_statuses = docusign_xml_parser(data)

        # Store the XML file on disk
        envelope_dir = os.path.join(
            settings.BASE_DIR, "media/docusign/", envelope_data["envelope_id"]
        )
        Path(envelope_dir).mkdir(parents=True, exist_ok=True)

        filename = (
            envelope_data["envelope_time_generated"].strftime("%Y%m%d_%H%M%S") + ".xml"
        )  # substitute _ for : for windows-land
        filepath = os.path.join(envelope_dir, filename)
        with open(filepath, "wb") as xml_file:
            xml_file.write(data)

    except Exception as e:
        msg = str(e)
        logger.exception(msg)
        return HttpResponse(msg)

    try:
        document = Document.objects.get(envelope_id=envelope_data["envelope_id"])
    except Document.DoesNotExist:
        message = 'O envelope {envelope_id} não existe.'.format(envelope_id=envelope_data["envelope_id"])
        logger.debug(message)
        return HttpResponse(message)
    else:
        # quando envia pelo localhost o webhook do docusign vai voltar a resposta para o test, por isso, não irá
        # encontrar o documento no banco
        envelope_status = str(envelope_data["envelope_status"]).lower()

        # variável para salvar o nome dos pdfs no signer_log
        pdf_filenames = ''

        tenant = Tenant.objects.get(pk=document.tenant.pk)
        # If the envelope is completed, pull out the PDFs from the notification XML an save on disk and send to GED
        if envelope_status == "completed":
            try:
                (envelope_data["pdf_documents"]) = docusign_pdf_files_saver(
                    data, envelope_dir
                )
                logger.debug(envelope_data)

                if tenant.plan.use_ged:
                    # Get document related interview data to post to GED
                    interview = Interview.objects.get(pk=document.interview.pk)
                    document_type_pk = interview.document_type.pk
                    document_language = interview.language

                    # Post documents to GED if envelope_status is completed
                    tenant_ged_data = TenantGedData.objects.get(pk=document.tenant.pk)
                    mc = MayanClient(tenant_ged_data.url, tenant_ged_data.token)

                    pdf_filenames = list()
                    for pdf in envelope_data["pdf_documents"]:
                        response = mc.document_create(
                            pdf["full_filename"],
                            document_type_pk,
                            pdf["filename"],
                            document_language,
                            pdf["description"],
                        )
                        logger.debug("Posting document to GED: " + pdf["filename"])
                        logger.debug(response.text)

                        pdf_filenames.append(pdf["filename"])

                    # separa os documentos com ENTER
                    pdf_filenames = chr(10).join(pdf_filenames)
            except Exception as e:
                msg = str(e)
                logger.exception(msg)
                return HttpResponse(msg)

        if envelope_status in envelope_vs_document_statuses.keys():
            document.status = envelope_vs_document_statuses[envelope_status]
        else:
            document.status = DocumentStatus.NAO_ENCONTRADO

        document.save()

        # se o log do envelope já existe atualiza status, caso contrário, cria o envelope
        try:
            envelope_log = EnvelopeLog.objects.get(document=document)
        except EnvelopeLog.DoesNotExist:
            envelope_log = EnvelopeLog(
                envelope_id=envelope_data['envelope_id'],
                status=envelope_data_translated['envelope_status'],
                envelope_created_date=envelope_data['envelope_created'],
                sent_date=envelope_data['envelope_sent'],
                status_update_date=envelope_data['envelope_time_generated'],
                document=document,
                tenant=tenant,
            )
            envelope_log.save()
        else:
            envelope_log.status = envelope_data_translated['envelope_status']
            envelope_log.status_update_date = envelope_data['envelope_time_generated']
            envelope_log.save(update_fields=['status', 'status_update_date'])

        for recipient_status in recipient_statuses:
            try:
                # se já tem o status para o email e para o envelope_log, não salva outro igual
                # só cria outro se o status do recipient mudou
                signer_log = SignerLog.objects.get(
                    envelope_log=envelope_log,
                    email=recipient_status['Email'],
                    status=recipient_status['Status'])
            except SignerLog.DoesNotExist:
                try:
                    signer_log = SignerLog(
                        name=recipient_status['UserName'],
                        email=recipient_status['Email'],
                        status=recipient_status['Status'],
                        sent_date=recipient_status['data_envio'],
                        type=recipient_status['Type'],
                        pdf_filenames=pdf_filenames,
                        envelope_log=envelope_log,
                        tenant=tenant,
                    )

                    signer_log.save()
                except Exception as e:
                    message = 'Não foi possível salvar o SignerLog: ' + str(e)
                    logger.exception(message)

    return HttpResponse("Success!")