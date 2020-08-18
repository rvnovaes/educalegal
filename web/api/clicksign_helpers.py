import hashlib
import hmac
import json
import logging
import os
import urllib.request

from pathlib import Path

from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from document.models import Document, Envelope, Signer, DocumentStatus
from interview.models import Interview
from tenant.models import Tenant, TenantGedData, ESignatureAppProvider

from .mayan_helpers import MayanClient


envelope_statuses = {
    "running": {"clicksign": "enviado", "el": DocumentStatus.ENVIADO_ASS_ELET.value},
    "closed": {"clicksign": "finalizado", "el": DocumentStatus.ASSINADO.value},
    "canceled": {"clicksign": "recusado", "el": DocumentStatus.RECUSADO_INVALIDO.value},
}

recipient_types = {
    "sign": "Assinar",
    "approve": "Assinar para aprovar",
    "party": "Assinar como parte",
    "witness": "Assinar como testemunha",
    "intervening": "Assinar como interveniente",
    "receipt": "Assinar para acusar recebimento",
    "endorser": "Assinar como endossante",
    "endorsee": "Assinar como endossatário",
    "administrator": "Assinar como administrador",
    "guarantor": "Assinar como avalista",
    "transferor": "Assinar como cedente",
    "transferee": "Assinar como cessionário",
    "contractee": "Assinar como contratada",
    "contractor": "Assinar como contratante",
    "joint_debtor": "Assinar como devedor solidário",
    "issuer": "Assinar como emitente",
    "manager": "Assinar como gestor",
    "buyer": "Assinar como parte compradora",
    "seller": "Assinar como parte vendedora",
    "attorney": "Assinar como procurador",
    "legal_representative": "Assinar como representante legal",
    "co_responsible": "Assinar como responsável solidário",
    "validator": "Assinar como validador",
    "ratify": "Assinar para homologar"
}

logger = logging.getLogger(__name__)

# if os.environ['EL_ENV'] == 'production':
#     secret_key = 'gerar no ambiente de producao'
# else:
#     secret_key = '6c49e1a0f98862bd735efec7548148b4'

# DEVELOPMENT - VER COMO PEGO O EL_ENV DO CONTAINER
secret_key = '6c49e1a0f98862bd735efec7548148b4'


def verify_hmac(headers, request_body):
    # Note: HTTP headers are case insensitive
    try:
        received_mac = headers.get('Content-Hmac')
        logging.info('received_mac')
        logging.info(received_mac)
    except Exception as e:
        logging.info('hmac 5')
        logging.info(e)

    if not received_mac:
        logging.info('hmac 6')
        logging.info("HMAC não foi fornecido.")
        return False

    key = secret_key.encode('utf-8')
    msg = str(request_body).encode('utf-8')

    logging.info('key')
    logging.info(key)

    logging.info('msg')
    logging.info(msg)

    generated_hmac = 'sha256=' + hmac.new(key=key, msg=msg, digestmod=hashlib.sha256).hexdigest()
    logging.info('hmac 7-2')

    match = hmac.compare_digest(received_mac, generated_hmac)

    logging.info('hmac 9')
    if not match:
        logging.info('HMACs não correspondem:')
        logging.info(received_mac)
        logging.info(generated_hmac)
        return False

    logging.info('hmac 11')
    return True


@require_POST
@csrf_exempt
def webhook_listener(request):
    try:
        # converte json para dict
        data = json.loads(request.body)

        # verifica se o webhook foi enviado pela Clicksign e que os dados nao estao comprometidos
        # HMAC é uma forma de verificar a integridade das informações transmitidas em um meio não confiável, i.e. a
        # Internet, através de uma chave secreta compartilhada entre as partes para validar as informações transmitidas.
        # logging.info('hmac 3')
        # if not verify_hmac(request.headers, request.body):
        #     return HttpResponse('HMACs não correspondem.')
        # logging.info('hmac 4')

        # localiza o documento pelo uuid
        envelope_number = data['document']['key']
        try:
            document = Document.objects.get(envelope_number=envelope_number)
        except Document.DoesNotExist:
            # quando envia pelo localhost o webhook do docusign vai voltar a resposta para o test,
            # por isso, não encontra o documento no banco
            message = 'O documento do envelope {envelope_number} não existe.'.format(
                envelope_number=envelope_number)
            logging.debug(message)
            return HttpResponse(message)
        except Exception as e:
            message = str(e)
            logging.exception(message)
            logging.info(message)
            return HttpResponse(message)
        else:
            envelope_status = str(data['document']['status']).lower()
            if envelope_status in envelope_statuses.keys():
                document_status = envelope_statuses[envelope_status]['el']
                envelope_status = envelope_statuses[envelope_status]['clicksign']
            else:
                document_status = DocumentStatus.NAO_ENCONTRADO.value
                envelope_status = DocumentStatus.NAO_ENCONTRADO.value

            filename = ''
            tenant = Tenant.objects.get(pk=document.tenant.pk)
            # If the envelope is completed, pull out the PDFs from the notification XML an save on disk and send to GED
            if envelope_status == "finalizado":
                fullpath, filename = pdf_file_saver(
                    data['document']['downloads']['signed_file_url'], envelope_number, document.name)

                if tenant.plan.use_ged:
                    # Get document related interview data to post to GED
                    interview = Interview.objects.get(pk=document.interview.pk)
                    document_type_pk = interview.document_type.pk
                    document_language = interview.language
                    document_description = interview.description if interview.description else ''

                    # Post documents to GED if envelope_status is completed
                    tenant_ged_data = TenantGedData.objects.get(pk=document.tenant.pk)
                    mc = MayanClient(tenant_ged_data.url, tenant_ged_data.token)

                    try:
                        # salva documento no ged
                        response = mc.document_create(
                            fullpath,
                            document_type_pk,
                            filename,
                            document_language,
                            document_description,
                        )
                        logging.debug("Posting document to GED: " + filename)
                        logging.debug(response.text)
                    except Exception as e:
                        message = str(e)
                        logging.exception(message)
                        logging.info(message)
                        return HttpResponse(message)

            # atualiza o status do documento
            document.status = document_status
            document.save(update_fields=['status'])

            # se o envelope já existe atualiza o status, caso contrário, cria o envelope
            try:
                envelope = Envelope.objects.get(identifier=envelope_number)
            except Envelope.DoesNotExist:
                envelope = Envelope(
                    identifier=envelope_number,
                    status=envelope_status,
                    envelope_created_date=data['document']['uploaded_at'],
                    sent_date=data['document']['uploaded_at'],
                    status_update_date=data['document']['updated_at'],
                    signing_provider=ESignatureAppProvider.CLICKSIGN.value,
                    tenant=tenant,
                )
                envelope.save()

                # vincula o envelope criado ao documento
                document.envelope = envelope
                document.envelope_number = envelope.identifier
                document.save(update_fields=['envelope', 'envelope_number'])
            else:
                envelope.status = envelope_status
                envelope.status_update_date = data['document']['updated_at']
                envelope.save(update_fields=['status', 'status_update_date'])

            recipient_status = None
            # define o status do recipient de acordo com o evento do webhook
            if data['event']['name'] == 'add_signer':
                recipient_status = 'criado'
            elif data['event']['name'] == 'sign':
                recipient_status = 'finalizado'
            elif data['event']['name'] == 'cancel':
                recipient_status = 'recusado'

            if recipient_status:
                for recipient in data['document']['signers']:
                    try:
                        # se já tem o status para o email e para o documento, não salva outro igual
                        # só cria outro se o status do recipient mudou
                        signer = Signer.objects.get(
                            document=document,
                            email=recipient['email'],
                            status=recipient_status)
                    except Signer.DoesNotExist:
                        create_signer = False
                        if recipient_status == 'criado' or recipient_status == 'recusado':
                            create_signer = True
                        elif recipient_status == 'finalizado':
                            # no evento sign vem uma tag 'signature' para o destinatario que assinou
                            for item in data['document']['signers']:
                                if recipient['email'] == item['email'] and 'signature' in item:
                                    create_signer = True

                        if create_signer:
                            try:
                                signer = Signer(
                                    name=recipient['name'],
                                    email=recipient['email'],
                                    status=recipient_status,
                                    sent_date=recipient['created_at'],
                                    type=recipient_types[recipient['sign_as']],
                                    pdf_filenames=filename,
                                    document=document,
                                    tenant=tenant,
                                )

                                signer.save()
                            except Exception as e:
                                message = 'Não foi possível salvar o Signer: ' + str(e)
                                logging.info(message)
                                logging.exception(message)
    except Exception as e:
        logging.info('Exceção webhook clicksign')
        logging.info(e)

    return HttpResponse("Success!")


def pdf_file_saver(url, envelope_number, document_name):
    # salva o pdf em media/clicksign
    envelope_dir = os.path.join(
        settings.BASE_DIR, "media/clicksign/", envelope_number
    )
    # cria diretorio e subdiretorio, caso nao exista
    Path(envelope_dir).mkdir(parents=True, exist_ok=True)

    # variável para salvar o nome dos pdfs no signer
    filename_no_extension = str(document_name.split(".pdf")[0])
    filename = filename_no_extension + '-assinado.pdf'
    fullpath = os.path.join(envelope_dir, filename)

    # baixa o pdf no diretorio criado
    urllib.request.urlretrieve(url, fullpath)

    return fullpath, filename
