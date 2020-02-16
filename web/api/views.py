import os
import json
import base64
from bs4 import BeautifulSoup
import logging

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import generics
from rest_framework import viewsets

from web.settings import BASE_DIR
from document.models import Document
from interview.models import Interview
from school.models import School
from tenant.models import Tenant

from .serializers import DocumentSerializer
from .serializers import InterviewSerializer
from .serializers import SchoolSerializer
from .serializers import TenantGEDSerializer

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
    body_unicode = request.body.decode('utf-8')
    data = json.loads(body_unicode)  # This is the entire incoming POST content.
    logger.info(data)
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
    envelope_dir = os.path.join(BASE_DIR, 'media/docusign/')
    filename = "T" + time_generated.replace(':', '_') + ".xml"  # substitute _ for : for windows-land
    filepath = os.path.join(envelope_dir, filename)
    with open(filepath, "w") as xml_file:
        xml_file.write(data)


    # If the envelope is completed, pull out the PDFs from the notification XML
    if (xml.EnvelopeStatus.Status.string == "Completed"):
        # Loop through the DocumentPDFs element, storing each document.
        for pdf in xml.DocumentPDFs.children:
            if (pdf.DocumentType.string == "CONTENT"):
                filename = 'Completed_' + pdf.Name.string
            elif (pdf.DocumentType.string == "SUMMARY"):
                filename = pdf.Name.string
            else:
                filename = pdf.DocumentType.string + "_" + pdf.Name.string
            full_filename = os.path.join(envelope_dir, filename)
            with open(full_filename, "wb") as pdf_file:
                pdf_file.write(base64.b64decode(pdf.PDFBytes.string))

    return HttpResponse("Success")


class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InterviewViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer


class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer


class TenantGEDViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list or retrieves a tenant. The serializer only returns a subset of fields necessary to run the
    interview so not to expose sensitive data.
    """

    queryset = Tenant.objects.all()
    serializer_class = TenantGEDSerializer


class TenantSchoolsViewList(generics.ListAPIView):
    serializer_class = SchoolSerializer

    def get_queryset(self):
        tid = self.kwargs["pk"]
        return School.objects.filter(tenant=tid)
