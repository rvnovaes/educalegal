import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status

from api.third_party.mayan_client import MayanClient
from billing.models import Plan
from document.models import Document, Envelope, Signer
from document.views import query_documents_by_args
from interview.models import Interview
from school.models import School
from tenant.models import Tenant, TenantGedData, ESignatureAppSignerKey

from .serializers import (
    DocumentSerializer,
    EnvelopeSerializer,
    ESignatureAppSignerKeySerializer,
    InterviewSerializer,
    PlanSerializer,
    SchoolSerializer,
    SignerSerializer,
    TenantSerializer,
    TenantGedDataSerializer
)


logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        status_code, message = self.verify_ged_settings()
        if status_code != status.HTTP_200_OK:
            return JsonResponse({"message": message}, status=status_code)
        else:
            return super(DocumentViewSet, self).create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        doc_uuid = kwargs["doc_uuid"]
        # doc_uuid = request.data["doc_uuid"]
        logger.info("Atualizando o documento {doc_uuid}".format(doc_uuid=str(doc_uuid)))
        instance = self.queryset.get(doc_uuid=doc_uuid)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        logger.debug(request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def verify_ged_settings(self):
        try:
            tenant_id = self.request.data['tenant']
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            message = 'A instância com ID = {} não foi encontrado.'.format(tenant_id)
            return status.HTTP_404_NOT_FOUND, message
        except Exception as e:
            message = str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return status.HTTP_400_BAD_REQUEST, message
        else:
            if tenant.has_ged():
                mc = MayanClient(tenant.tenantgeddata.url, tenant.tenantgeddata.token)

                try:
                    interview_id = self.request.data['interview']
                    interview = Interview.objects.get(pk=interview_id)
                except Interview.DoesNotExist:
                    message = 'A entrevista com ID = {} não foi encontrada.'.format({interview_id})
                    return status.HTTP_404_NOT_FOUND, message
                except Exception as e:
                    message = str(type(e).__name__) + " : " + str(e)
                    logger.error(message)
                    return status.HTTP_400_BAD_REQUEST, message

                document_type_id = interview.document_type_id

                # verifica se existe no ged o tipo de documento da entrevista selecionada
                try:
                    document_type_data = mc.document_type_read(document_type_id)
                except Exception as e:
                    message = str(type(e).__name__) + " : " + str(e)
                    logger.error(message)
                    return status.HTTP_400_BAD_REQUEST, message
                else:
                    if 'detail' in document_type_data:
                        if document_type_data['detail'] == 'Invalid token.':
                            message = 'O token do usuário do Mayan está inválido ou não existe.'
                            return status.HTTP_404_NOT_FOUND, message

                        # json_encode($response, JSON_UNESCAPED_UNICODE);
                        if (document_type_data['detail'] == 'Not found.') or \
                                (document_type_data['detail'] == 'N\u00e3o encontrado.'):
                            message = 'Não existe o tipo de documento com ID = {} cadastrado no Mayan.'.format(
                                document_type_id)

                            return status.HTTP_404_NOT_FOUND, message
        return status.HTTP_200_OK, 'Configuração do GED OK'


class EnvelopeViewSet(viewsets.ModelViewSet):
    queryset = Envelope.objects.all()
    serializer_class = EnvelopeSerializer


class SignerViewSet(viewsets.ModelViewSet):
    queryset = Signer.objects.all()
    serializer_class = SignerSerializer

    def create(self, request, *args, **kwargs):
        """
        Cria um novo log do assinante (signer).
        """
        # By default, Django Rest Framework assumes you are passing it a single object.
        # To serialize a queryset or list of objects instead of a single object instance,
        # you should pass the many=True flag when instantiating the serializer.
        # You can then pass a queryset or list of objects to be serialized.
        many = True if isinstance(request.data, list) else False

        serializer = self.get_serializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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


class ESignatureAppSignerKeyViewSet(viewsets.ModelViewSet):
    serializer_class = ESignatureAppSignerKeySerializer
    # default 'pk', se quiser pesquisar por outro campo deve alterar o lookup_field
    lookup_field = 'email'

    def get_queryset(self):
        # deve ser usada a funcao filter e nao a get para que seja retornado um queryset e nao um
        # ESignatureAppSignerKey
        # como cada cliente tem uma conta da clicksign, deve ser verificado o tenant tbm
        # como tem ambiente de producao e homologacao, verificar esignature_app
        # como o mesmo email pode ser usado por pessoas diferentes na entrevista (email de PJ), verificar nome

        return ESignatureAppSignerKey.objects.filter(
            tenant=self.request.user.tenant.id,
            esignature_app=self.request.user.tenant.esignature_app,
            email=self.kwargs['email'],
            name=self.kwargs['name'])
