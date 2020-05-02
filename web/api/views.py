import os
from pathlib import Path
import base64
import xmltodict
from requests import Session
from retry_requests import retry
import logging
from datetime import datetime as dt

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework import viewsets

from web.settings import BASE_DIR
from document.models import Document, DocumentESignatureLog
from interview.models import Interview
from school.models import School
from tenant.models import Tenant, TenantGedData, TenantESignatureData

from .serializers import DocumentSerializer
from .serializers import InterviewSerializer
from .serializers import SchoolSerializer
from .serializers import (
    TenantSerializer,
    TenantGedDataSerializer,
    TenantESignatureDataSerializer,
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


def docusign_xml_parser(data):
    envelope_data = dict()
    xml = xmltodict.parse(data)["DocuSignEnvelopeInformation"]
    envelope_data["envelope_id"] = xml["EnvelopeStatus"]["EnvelopeID"]
    envelope_data["envelope_status"] = xml["EnvelopeStatus"]["Status"]
    envelope_data["envelope_created"] = xml["EnvelopeStatus"]["Created"]
    envelope_data["envelope_sent"] = xml["EnvelopeStatus"]["Sent"]
    envelope_data["envelope_time_generated"] = xml["EnvelopeStatus"]["TimeGenerated"]

    envelope_data_translated = envelope_data.copy()

    #formatting strings: 2020-04-15T11:20:19.693
    envelope_data_translated['envelope_created'] = envelope_data_translated['envelope_created'].replace("T", " ").split(".")[0]
    envelope_data_translated['envelope_sent'] = envelope_data_translated['envelope_sent'].replace("T", " ").split(".")[0]
    envelope_data_translated['envelope_time_generated'] = envelope_data_translated['envelope_time_generated'].replace("T", " ").split(".")[0]

    #converting US dates to Brazil dates
    envelope_data_translated['envelope_created'] = str(dt.strptime(envelope_data_translated['envelope_created'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))
    envelope_data_translated['envelope_sent'] = str(dt.strptime(envelope_data_translated['envelope_sent'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))
    envelope_data_translated['envelope_time_generated'] = str(dt.strptime(envelope_data_translated['envelope_time_generated'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S'))

    envelope_data_translated["envelope_status"] = str(envelope_data_translated["envelope_status"]).lower()
    if envelope_data_translated["envelope_status"] in envelope_statuses.keys():
        envelope_data_translated["envelope_status"] = envelope_statuses[envelope_data_translated["envelope_status"]]
    else:
        envelope_data_translated["envelope_status"] = 'não encontrado'

    e_status_detail = (
        "ID do envelope: "
        + envelope_data_translated["envelope_id"]
        + "<br>"
        + "Status do envelope: "
        + envelope_data_translated["envelope_status"]
        + "<br>"
        + "Data de criação: "
        + envelope_data_translated["envelope_created"]
        + "<br>"
        + "Data de envio: "
        + envelope_data_translated["envelope_sent"]
        + "<br>"
        + "Criação do envelope: "
        + envelope_data_translated["envelope_time_generated"]
        + "<br>"
    )
    envelope_data["envelope_status_detail_message"] = e_status_detail
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

    r_status_detail = ""
    for r in recipient_statuses:
        r_status_detail += (
            r["RoutingOrder"]
            + " - "
            + r["UserName"]
            + " - "
            + r["Email"]
            + " - "
            + r["Type"]
            + " - "
            + r["Status"]
            + "<br>"
        )
    envelope_data["envelope_recipient_status_detail_message"] = r_status_detail
    all_details = (
        "<b> Detalhes do Envelope </b><br>"
        + e_status_detail
        + "<br>"
        + "<b> Detalhes dos Destinatários </b><br>"
        + r_status_detail
        + "<br>"
    )
    envelope_data["envelope_all_details_message"] = all_details
    return envelope_data

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
        envelope_data = docusign_xml_parser(
            data
        )  # Parses XML data and returns a dictionary and formated messages
        logger.debug(envelope_data["envelope_id"])
        logger.debug(envelope_data["envelope_time_generated"])
        logger.debug(envelope_data["envelope_all_details_message"])

        # Store the XML file on disk
        envelope_dir = os.path.join(
            BASE_DIR, "media/docusign/", envelope_data["envelope_id"]
        )
        Path(envelope_dir).mkdir(parents=True, exist_ok=True)
        filename = (
            envelope_data["envelope_time_generated"].replace(":", "_") + ".xml"
        )  # substitute _ for : for windows-land
        logger.debug(envelope_data)
        filepath = os.path.join(envelope_dir, filename)
        with open(filepath, "wb") as xml_file:
            xml_file.write(data)

    except Exception as e:
        msg = str(e)
        logger.exception(msg)
        return HttpResponse(msg)

    document = Document.objects.get(envelope_id=envelope_data["envelope_id"])
    envelope_status = str(envelope_data["envelope_status"]).lower()

    tenant = Tenant.objects.get(pk=document.tenant.pk)
    # If the envelope is completed, pull out the PDFs from the notification XML an save on disk and send to GED
    if envelope_status == "completed" and tenant.use_ged:
        try:
            (envelope_data["pdf_documents"]) = docusign_pdf_files_saver(
                data, envelope_dir
            )
            logger.debug(envelope_data)

            # Get document related interview data to post to GED
            interview = Interview.objects.get(pk=document.interview.pk)
            document_type_pk = interview.document_type.pk
            document_language = interview.language

            # Post documents to GED
            tenant_ged_data = TenantGedData.objects.get(pk=document.tenant.pk)
            mc = MayanClient(tenant_ged_data.url, tenant_ged_data.token)

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

        except Exception as e:
            msg = str(e)
            logger.exception(msg)
            return HttpResponse(msg)

    if envelope_status in envelope_statuses.keys():
        document.status = envelope_statuses[envelope_status]
    else:
        document.status = "não encontrado"

    if envelope_status == "completed":
        log = ""
        for pdf in envelope_data["pdf_documents"]:
            log += pdf["filename"] + "<br>"

        log += "<br>"
        esignature_log_documents = DocumentESignatureLog(
            esignature_log=log, document=document,
        )
        esignature_log_documents.save()

    esignature_log_messages = DocumentESignatureLog(
        esignature_log=envelope_data["envelope_all_details_message"], document=document,
    )
    esignature_log_messages.save()

    document.save()

    return HttpResponse("Success!")


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def partial_update(self, request, *args, **kwargs):
        el_document_id = request.data["el_document_created_id"]
        instance = self.queryset.get(pk=el_document_id)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer


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


class TenantESignatureDataViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TenantESignatureDataSerializer

    def get_queryset(self):
        return TenantESignatureData.objects.filter(tenant=self.kwargs["pk"])
