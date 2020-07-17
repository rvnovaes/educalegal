import logging

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status

from billing.models import Plan
from document.models import Document, EnvelopeLog, SignerLog
from document.views import query_documents_by_args
from interview.models import Interview
from school.models import School
from tenant.models import Tenant, TenantGedData

from .serializers import (
    DocumentSerializer,
    EnvelopeLogSerializer,
    InterviewSerializer,
    PlanSerializer,
    SchoolSerializer,
    SignerLogSerializer,
    TenantSerializer,
    TenantGedDataSerializer
)


logger = logging.getLogger(__name__)


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


class EnvelopeLogViewSet(viewsets.ModelViewSet):
    queryset = EnvelopeLog.objects.all()
    serializer_class = EnvelopeLogSerializer
    logging.info('api 0')

    def create(self, request, *args, **kwargs):
        logging.info('api 01')
        """
        Cria um novo log do envelope (envelope log), caso não exista.
        Se já existir, retorna o envelope log encontrado.
        """

        try:
            document = Document.objects.filter(doc_uuid=self.kwargs['uuid']).first()
            logging.info('api 1')
            logging.info(document.id)
        except Exception as e:
            message = 'O documento {doc_uuid} não existe.'.format(doc_uuid=self.kwargs['uuid'])
            logger.debug(message)
            logger.debug(e)
            logging.info('api 2')
        else:
            envelope_log = EnvelopeLog.objects.filter(document=document).first()
            # insere o id do documento no dict do envelope
            data_complete = request.data.copy()
            data_complete['document'] = document.id
            serializer = self.get_serializer(data=data_complete)
            serializer.is_valid(raise_exception=True)
            logging.info('api 3')

            if envelope_log:
                logging.info('api 4')
                logging.info(envelope_log)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                logging.info('api 5')
                self.perform_create(serializer)
                return Response(serializer.data, status=status.HTTP_201_CREATED)


class SignerLogViewSet(viewsets.ModelViewSet):
    queryset = SignerLog.objects.all()
    serializer_class = SignerLogSerializer

    def create(self, request, *args, **kwargs):
        """
        Cria um novo log do assinante (signer log).
        """
        envelope_log = EnvelopeLog.objects.get(pk=request.data['id'])
        request.data['envelope_log'] = envelope_log
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
    def list(self, request, **kwargs):
        try:
            document = query_documents_by_args(self.kwargs['pk'], **request.query_params)

            serializer = DocumentSerializer(document['items'], many=True)
            result = dict()
            result['data'] = serializer.data
            result['draw'] = document['draw']
            result['recordsTotal'] = document['total']
            result['recordsFiltered'] = document['count']
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(e)

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
