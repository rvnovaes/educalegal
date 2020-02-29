import os
from pathlib import Path
import base64
import xmltodict

import logging

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

logger = logging.getLogger(__name__)


def docusign_xml_parser(data):
    envelope_data = dict()
    xml = xmltodict.parse(data)["DocuSignEnvelopeInformation"]
    envelope_data["envelope_id"] = xml["EnvelopeStatus"]["EnvelopeID"]
    envelope_data["envelope_status"] = xml["EnvelopeStatus"]["Status"]
    envelope_data["envelope_created"] = xml["EnvelopeStatus"]["Created"]
    envelope_data["envelope_sent"] = xml["EnvelopeStatus"]["Sent"]
    envelope_data["envelope_time_generated"] = xml["EnvelopeStatus"]["TimeGenerated"]

    e_status_detail = (
        "Envelope ID: "
        + envelope_data["envelope_id"]
        + "\n"
        + "Envelope Status: "
        + envelope_data["envelope_status"]
        + "\n"
        + "Envelope Created: "
        + envelope_data["envelope_created"]
        + "\n"
        + "Envelope Sent: "
        + envelope_data["envelope_sent"]
        + "\n"
        + "Time Generated: "
        + envelope_data["envelope_time_generated"]
        + "\n"
    )
    envelope_data["envelope_status_detail_message"] = e_status_detail
    recipient_statuses = xml["EnvelopeStatus"]["RecipientStatuses"]["RecipientStatus"]

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
            + "\n"
        )
    envelope_data["envelope_recipient_status_detail_message"] = r_status_detail
    all_details = (
        "### Detalhes do Envelope ###\n"
        + e_status_detail
        + "\n"
        + "### Detalhes dos Destinatários ###\n"
        + r_status_detail
        + "\n"
    )
    envelope_data["envelope_all_details_message"] = all_details
    return envelope_data


def docusign_pdf_files_saver(data, envelope_dir):
    pdf_documents = list()
    xml = xmltodict.parse(data)["DocuSignEnvelopeInformation"]
    # Loop through the DocumentPDFs element, storing each document.
    for pdf in xml["DocumentPDFs"]["DocumentPDF"]:
        if pdf["DocumentType"] == "CONTENT":
            filename = "Completed_" + pdf["Name"]
        elif pdf["DocumentType"] == "SUMMARY":
            filename = pdf["Name"]
        else:
            filename = pdf["DocumentType"] + "_" + pdf["Name"]
        pdf_documents.append(filename)

        full_filename = os.path.join(envelope_dir, filename)
        with open(full_filename, "wb") as pdf_file:
            pdf_file.write(base64.b64decode(pdf["PDFBytes"]))
    return pdf_documents


@require_POST
@csrf_exempt
def docusign_webhook_listener(request):
    logger.info(request.headers)
    logger.info(request.content_type)
    data = request.body  # This is the entire incoming POST content in Django
    try:
        envelope_data = docusign_xml_parser(
            data
        )  # Parses XML data and returns a dictionary and formated messages
        logger.info(envelope_data["envelope_id"])
        logger.info(envelope_data["envelope_time_generated"])
        logger.debug(envelope_data["envelope_all_details_message"])

        # Store the XML file on disk
        envelope_dir = os.path.join(
            BASE_DIR, "media/docusign/", envelope_data["envelope_id"]
        )
        Path(envelope_dir).mkdir(parents=True, exist_ok=True)
        filename = (
            envelope_data["envelope_time_generated"].replace(":", "_") + ".xml"
        )  # substitute _ for : for windows-land
        filepath = os.path.join(envelope_dir, filename)
        with open(filepath, "wb") as xml_file:
            xml_file.write(data)

    except Exception as e:
        msg = str(e)
        logger.exception(msg)
        return HttpResponse(msg)

    # If the envelope is completed, pull out the PDFs from the notification XML
    if envelope_data["envelope_status"] == "Completed":
        try:
            envelope_data["pdf_documents "] = docusign_pdf_files_saver(
                data, envelope_dir
            )
        except Exception as e:
            msg = str(e)
            logger.exception(msg)
            return HttpResponse(msg)

    logger.debug(envelope_data)

    # Updates Main Document Status
    main_document = Document.objects.get(
        main_document=True, envelope_id=envelope_data["envelope_id"]
    )
    main_document.status = envelope_data["envelope_status"]
    esignature_log = DocumentESignatureLog(
        esignature_log=envelope_data["envelope_all_details_message"],
        document=main_document,
    )
    esignature_log.save()
    main_document.save()

    return HttpResponse("Success!")


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def partial_update(self, request, *args, **kwargs):
        ged_id = request.data["ged_id"]
        instance = self.queryset.get(ged_id=ged_id)
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
