import os
from pathlib import Path
import base64
from bs4 import BeautifulSoup
import logging

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from rest_framework.response import Response
from rest_framework import generics
from rest_framework import viewsets

from web.settings import BASE_DIR
from document.models import Document
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


@require_POST
@csrf_exempt
def docusign_webhook_listener(request):
    # Process the incoming webhook data. See the DocuSign Connect guide
    # for more information
    #
    # Strategy: examine the data to pull out the envelope_id and time_generated fields.
    # Then store the entire xml on our local file system using those fields.
    #
    # If the envelope status=="Completed" then store the files as doc1.pdf, doc2.pdf, etc
    #
    # This function could also enter the data into a dbms, add it to a queue, etc.
    # Note that the total processing time of this function must be less than
    # 100 seconds to ensure that DocuSign's request to your app doesn't time out.
    # Tip: aim for no more than a couple of seconds! Use a separate queuing service
    # if need be.
    logger.info(request.headers)
    logger.info(request.content_type)
    # logger.info(request.body)
    # body_unicode = request.body.decode('utf-8')
    # data = json.loads(body_unicode)  # This is the entire incoming POST content.
    # logger.info(body_unicode)
    data = request.body  # This is the entire incoming POST content.
    # This is dependent on your web server. In this case, Flask

    # f = open(os.getcwd() + "/app/example_completed_notification.xml")
    # data = f.read()

    # Note, there are many options for parsing XML in Python
    # For this recipe, we're using Beautiful Soup, http://www.crummy.com/software/BeautifulSoup/

    xml = BeautifulSoup(data, "xml")
    envelope_id = xml.EnvelopeStatus.EnvelopeID.string
    logger.info(envelope_id)
    time_generated = xml.EnvelopeStatus.TimeGenerated.string
    logger.info(time_generated)

    # Store the file.
    # Some systems might still not like files or directories to start with numbers.
    # So we prefix the envelope ids with E and the timestamps with T
    envelope_dir = os.path.join(BASE_DIR, "media/docusign/", envelope_id)
    Path(envelope_dir).mkdir(parents=True, exist_ok=True)
    filename = (
        "T" + time_generated.replace(":", "_") + ".xml"
    )  # substitute _ for : for windows-land
    filepath = os.path.join(envelope_dir, filename)
    with open(filepath, "wb") as xml_file:
        xml_file.write(data)

    # If the envelope is completed, pull out the PDFs from the notification XML
    if xml.EnvelopeStatus.Status.string == "Completed":
        # Loop through the DocumentPDFs element, storing each document.
        for pdf in xml.DocumentPDFs.children:
            if pdf.DocumentType.string == "CONTENT":
                filename = "Completed_" + pdf.Name.string
            elif pdf.DocumentType.string == "SUMMARY":
                filename = pdf.Name.string
            else:
                filename = pdf.DocumentType.string + "_" + pdf.Name.string
            full_filename = os.path.join(envelope_dir, filename)
            with open(full_filename, "wb") as pdf_file:
                pdf_file.write(base64.b64decode(pdf.PDFBytes.string))

    return HttpResponse("Success")


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def partial_update(self, request, *args, **kwargs):
        ged_id = request.data['ged_id']
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

