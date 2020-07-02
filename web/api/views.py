import datetime as dt
from datetime import datetime

import os
from pathlib import Path
import base64
import xmltodict
from requests import Session
from retry_requests import retry
import logging

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework import viewsets

from django.conf import settings

from billing.models import Plan
from document.models import Document, EnvelopeLog, SignerLog
from interview.models import Interview
from school.models import School
from tenant.models import Tenant, TenantGedData

from .serializers import (
    DocumentSerializer,
    InterviewSerializer,
    PlanSerializer,
    SchoolSerializer,
    TenantSerializer,
    TenantGedDataSerializer
)
from .docusign_translations import envelope_statuses, recipient_statuses_dict, recipient_types_dict

logger = logging.getLogger(__name__)


class MayanClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=0.5,
            status_to_retry=(500, 502, 504, 404),
        )
        self.session.headers.update(headers)

    def document_create(
        self, filename, document_type, label="", language="", description=""
    ):
        file_object = open(filename, mode="rb")
        payload = {
            "document_type": document_type,
            "label": label,
            "language": language,
            "description": description,
        }
        final_url = self.api_base_url + "/api/documents/"
        response = self.session.post(
            final_url, data=payload, files={"file": file_object}
        )
        return response


def _iso8601_to_datetime(iso8601_date):
    # tamanho máximo de casas dedimais aceitas pelo python é 6
    # https://docs.python.org/3/library/datetime.html
    # Microsecond as a decimal number, zero-padded on the left (accepts from one to six digits)
    # quando vier mais do que 6, trunca em 6
    # Ex.: '2020-06-29T19:03:46.4619595' >> '2020-06-29T19:03:46.461959'
    iso8601_date = iso8601_date[:26]
    # tenta converter a data do docusign que vem no formato ISO 8601 para datetime
    try:
        converted_datetime = datetime.fromisoformat(iso8601_date)
    except:
        # se a data não veio no formato certo (ISO 8601), converte manualmente
        # iso8601_date = iso8601_date.strftime('%d/%m/%Y %H:%M:%S.%f')
        converted_datetime = dt.datetime.strptime(iso8601_date, '%Y-%m-%dT%H:%M:%S.%f')

    return converted_datetime


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
    envelope_data['envelope_created'] = _iso8601_to_datetime(envelope_data['envelope_created'])
    envelope_data['envelope_sent'] = _iso8601_to_datetime(envelope_data['envelope_sent'])
    envelope_data['envelope_time_generated'] = _iso8601_to_datetime(envelope_data['envelope_time_generated'])

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
        envelope_data_translated["envelope_status"] = 'não encontrado'

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
            recipient_status['data_envio'] = _iso8601_to_datetime(recipient_status['Sent'])
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

        # If the envelope is completed, pull out the PDFs from the notification XML an save on disk and send to GED
        if envelope_status == "completed":
            try:
                (envelope_data["pdf_documents"]) = docusign_pdf_files_saver(
                    data, envelope_dir
                )
                logger.debug(envelope_data)

                tenant = Tenant.objects.get(pk=document.tenant.pk)
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

        if envelope_status in envelope_statuses.keys():
            document.status = envelope_statuses[envelope_status]
        else:
            document.status = "não encontrado"

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
                    )

                    signer_log.save()
                except Exception as e:
                    message = 'Não foi possível salvar o SignerLog: ' + str(e)
                    logger.exception(message)

    return HttpResponse("Success!")


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def partial_update(self, request, *args, **kwargs):
        doc_uuid = request.data["doc_uuid"]
        logger.info("Atualizando o documento {doc_uuid}".format(doc_uuid=str(doc_uuid)))
        instance = self.queryset.get(doc_uuid=doc_uuid)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        logger.debug(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer


class TenantSchoolViewSet(viewsets.ViewSet):
    def list(self, request, pk=None):
        queryset = School.objects.filter(tenant=pk)
        serializer = SchoolSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, spk=None):
        queryset = School.objects.all()
        school = get_object_or_404(queryset, id=spk, tenant=pk)
        serializer = SchoolSerializer(school)
        return Response(serializer.data)


class TenantInterviewViewSet(viewsets.ViewSet):
    def list(self, request, pk=None):
        queryset = Interview.objects.filter(tenants=pk)
        serializer = InterviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, spk=None):
        queryset = Interview.objects.all()
        interview = get_object_or_404(queryset, id=spk, tenants=pk)
        serializer = SchoolSerializer(interview)
        return Response(serializer.data)


class TenantDocumentViewSet(viewsets.ViewSet):
    def list(self, request, pk=None):
        queryset = Document.objects.filter(tenant=pk)
        serializer = DocumentSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, spk=None):
        queryset = Document.objects.all()
        interview = get_object_or_404(queryset, id=spk, tenant=pk)
        serializer = DocumentSerializer(interview)
        return Response(serializer.data)


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list or retrieves a tenant.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


class TenantGedDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TenantGedDataSerializer

    def get_queryset(self):
        return TenantGedData.objects.filter(tenant=self.kwargs["pk"])