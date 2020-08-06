import base64
import hashlib
import hmac
import logging
import os
import urllib.request

from pathlib import Path

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings

from document.models import Document, Envelope, Signer, DocumentStatus
from interview.models import Interview
from tenant.models import Tenant, TenantGedData, ESignatureAppProvider

from .mayan_helpers import MayanClient


envelope_statuses = {
    "running": {"clicksign": "enviado", "el": DocumentStatus.ENVIADO_ASS_ELET.value},
    "closed": {"clicksign": "finalizado", "el": DocumentStatus.ASSINADO.value},
    "cancel": {"clicksign": "recusado", "el": DocumentStatus.RECUSADO_INVALIDO.value},
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


def verify_hmac(headers: dict, request_data: bytes, secret_key: str):
    # Note: HTTP headers are case insensitive
    # alg = headers.get('kindly-hmac-algorithm')
    mac = headers.get('Content-Hmac')

    'Content-Hmac: sha256=20dbdb06a522fb5046722c671bcf31f12be45485c425b6652c940546c397ea53'

    print(headers)

    # if not (alg and mac):
    #     print("HMAC was not provided")
    #     return False
    #
    # if alg != "HMAC-SHA-256 (base64 encoded)":
    #     print("Unexpected HMAC algorithm")
    #     return False

    msg = request_data
    key = secret_key.encode('utf-8')

    received_hmac_b64 = mac.encode('utf-8')
    generated_hmac = hmac.new(key=key, msg=msg, digestmod=hashlib.sha256).digest()
    generated_hmac_b64 = base64.b64encode(generated_hmac)

    match = hmac.compare_digest(received_hmac_b64, generated_hmac_b64)

    if not match:
        print('HMACs did not match: {} {}'.format(received_hmac_b64, generated_hmac_b64))
        return False

    return True


@require_POST
@csrf_exempt
def webhook_listener(request):
    data = request.body  # This is the entire incoming POST content in Django

    logging.info('passou aqui 1')

    # ignora o evento add_signer, pois nao tem nenhuma informacao nova
    if data['event']['name'] == 'add_signer':
        logging.info('passou aqui 2')
        return HttpResponse("Success!")

    # localiza o documento pelo uuid
    envelope_number = data['document']['key']
    logging.info('passou aqui 3')
    logging.info(envelope_number)
    try:
        logging.info('passou aqui 4')
        document = Document.objects.get(envelope_number=envelope_number)
    except Document.DoesNotExist:
        logging.info('passou aqui 5')
        # quando envia pelo localhost o webhook do docusign vai voltar a resposta para o test,
        # por isso, não encontra o documento no banco
        message = 'O documento do envelope {envelope_number} não existe.'.format(
            envelope_number=envelope_number)
        logger.debug(message)
        return HttpResponse(message)
    except Exception as e:
        logging.info('passou aqui 6')
        message = str(e)
        logger.exception(message)
        logging.info(message)
        return HttpResponse(message)
    else:
        logging.info('passou aqui 7')
        envelope_status = str(data['document']['status']).lower()
        if envelope_status in envelope_statuses.keys():
            envelope_status = envelope_statuses[envelope_status]['clicksign']
            document_status = envelope_statuses[envelope_status]['el']
        else:
            envelope_status = DocumentStatus.NAO_ENCONTRADO.value
            document_status = DocumentStatus.NAO_ENCONTRADO.value

        filename = ''
        tenant = Tenant.objects.get(pk=document.tenant.pk)
        logging.info('passou aqui 8')
        logging.info(envelope_status)
        logging.info(document_status)
        # If the envelope is completed, pull out the PDFs from the notification XML an save on disk and send to GED
        if envelope_status == "finalizado":
            logging.info('passou aqui 9')
            fullpath, filename = pdf_file_saver(data['document']['signed_file_url'], envelope_number, document.name)

            if tenant.plan.use_ged:
                logging.info('passou aqui 10')
                # Get document related interview data to post to GED
                interview = Interview.objects.get(pk=document.interview.pk)
                document_type_pk = interview.document_type.pk
                document_language = interview.language
                document_description = interview.description if interview.description else ''

                # Post documents to GED if envelope_status is completed
                tenant_ged_data = TenantGedData.objects.get(pk=document.tenant.pk)
                mc = MayanClient(tenant_ged_data.url, tenant_ged_data.token)

                logging.info('passou aqui 11')
                try:
                    logging.info('passou aqui 12')
                    # salva documento no ged
                    response = mc.document_create(
                        fullpath,
                        document_type_pk,
                        filename,
                        document_language,
                        document_description,
                    )
                    logger.debug("Posting document to GED: " + filename)
                    logger.debug(response.text)
                except Exception as e:
                    logging.info('passou aqui 13')
                    message = str(e)
                    logger.exception(message)
                    logging.info(message)
                    return HttpResponse(message)

        # atualiza o status do documento
        document.status = document_status
        document.save(update_fields=['status'])

        logging.info('passou aqui 14')
        # se o envelope já existe atualiza o status, caso contrário, cria o envelope
        try:
            logging.info('passou aqui 15')
            envelope = Envelope.objects.get(identifier=envelope_number)
        except Envelope.DoesNotExist:
            logging.info('passou aqui 16')
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
            logging.info('passou aqui 17')
            envelope.status = envelope_status
            envelope.status_update_date = data['document']['updated_at']
            envelope.save(update_fields=['status', 'status_update_date'])

        # define o status do recipient de acordo com o evento do webhook
        if data['event']['name'] == 'upload':
            # no evento upload vem o documento e os destinatarios vinculados
            recipient_status = 'criado'
        elif data['event']['name'] == 'sign':
            recipient_status = 'finalizado'

        logging.info('passou aqui 18')
        logging.info(recipient_status)
        for recipient in data['document']['signers']:
            try:
                logging.info('passou aqui 19')
                # se já tem o status para o email e para o documento, não salva outro igual
                # só cria outro se o status do recipient mudou
                signer = Signer.objects.get(
                    document=document,
                    email=recipient['email'],
                    status=recipient_status)
            except Signer.DoesNotExist:
                logging.info('passou aqui 20')
                create_signer = False
                if recipient_status == 'criado':
                    create_signer = True
                elif recipient_status == 'finalizado':
                    # no evento sign vem uma tag 'signature' para o destinatario que assinou
                    if 'signature' in data['document']['signers']:
                        create_signer = True

                if create_signer:
                    try:
                        logging.info('passou aqui 21')
                        signer = Signer(
                            name=recipient['name'],
                            email=recipient['email'],
                            status=recipient_status,
                            sent_date=recipient['created_at'],
                            type=recipient_types[recipient['sign_as']],
                            filenames=filename,
                            document=document,
                            tenant=tenant,
                        )

                        signer.save()
                    except Exception as e:
                        logging.info('passou aqui 22')
                        message = 'Não foi possível salvar o Signer: ' + str(e)
                        logging.info(message)
                        logger.exception(message)

    logging.info('passou aqui 23')
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
