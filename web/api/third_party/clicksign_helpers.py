import hashlib
import hmac
import json
import logging
import os
import urllib.request

from copy import deepcopy
from pathlib import Path

from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from api.views_v2 import save_in_ged
from document.models import Document, Envelope, Signer, DocumentStatus, DocumentFileKind
from document.views import save_document_data
from interview.models import Interview
from tenant.models import Tenant, TenantGedData, ESignatureAppProvider


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


def verify_hmac(headers, request_body, test_mode):
    if test_mode:
        secret_key = '3d46fb2ab42bb79822d7294923bc071b'
    else:
        secret_key = '49bc7fbfbe3e41188c0cd5ce679eff56'

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
            return HttpResponse(status=400, reason=message)
        except Exception as e:
            message = str(e)
            logging.exception(message)
            logging.info(message)
            return HttpResponse(status=400, reason=message)
        else:
            # verifica se o webhook foi enviado pela Clicksign e que os dados nao estao comprometidos
            # HMAC é uma forma de verificar a integridade das informações transmitidas em um meio não confiável, i.e. a
            # Internet, através de uma chave secreta compartilhada entre as partes para validar as informações transmitidas.
            # logging.info('hmac 3')
            # if not verify_hmac(request.headers, request.body, document.tenant.esignature_app.test_mode):
            #     return HttpResponse(status=400, reason='HMACs não correspondem.')
            # logging.info('hmac 4')

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
            logging.info('passou_aqui_1')
            if envelope_status == "finalizado":
                # ao finalizar as assinaturas do documento estou recebendo um request.body sem a url do pdf assinado
                # resposta do suporte da clicksign: Quando o evento auto_close é disparado pela primeira vez, alguns
                # processos ainda são feitos internamente para que o documento assinado esteja pronto.
                # Dessa forma, é possível que ao receber o primeiro evento, a cópia final ainda não esteja disponível.
                # Sendo assim, recomendamos que a primeira tentativa seja recusada, ou que o evento só seja aceito com
                # URL documento assinado.
                if 'signed_file_url' not in data['document']['downloads']:
                    logging.info('Ignora requisição, pois evento {} não contém a chave signed_file_url'.format(
                        data['event']['name']))
                    return HttpResponse(status=400, reason='Falta a chave signed_file_url')

                logging.info('signed_file_url')
                logging.info(data)
                relative_path = "clicksign/" + str(envelope_number)
                fullpath, filename = pdf_file_saver(
                    data['document']['downloads']['signed_file_url'], envelope_number, document.name)

                relative_file_path = os.path.join(relative_path, filename)
                logging.info('passou_aqui_relative_file_path')
                logging.info(relative_file_path)

                logging.info('passou_aqui_2')
                has_ged = tenant.has_ged()
                if has_ged:
                    # Get document related interview data to post to GED
                    interview = Interview.objects.get(pk=document.interview.pk)
                    document_description = interview.description if interview.description else ''

                    post_data = {
                        "description": document_description,
                        "document_type": interview.document_type.pk,
                        "language": interview.language,
                    }

                    try:
                        logging.info('passou_aqui_3')
                        # salva documento no ged
                        post_data["label"] = filename
                        status_code, ged_data, ged_id = save_in_ged(post_data, fullpath, document.tenant)
                    except Exception as e:
                        logging.info('passou_aqui_4')
                        message = str(e)
                        logging.exception(message)
                        return HttpResponse(status=400, reason=message)
                    else:
                        logging.info('passou_aqui_5')
                        logging.debug("Posting document to GED: " + filename)
                        logging.debug(ged_data)

                        if status_code == 201:
                            logging.info('passou_aqui_6')
                            # salva o documento baixado no EL como documento relacionado
                            related_document = deepcopy(document)
                            related_document.name = filename
                            related_document.file_kind = DocumentFileKind.PDF_SIGNED.value
                            save_document_data(related_document, has_ged, ged_data, relative_path, document)
                        else:
                            logging.info('passou_aqui_7')
                            message = 'Não foi possível salvar o documento no GED. {} - {}'.format(
                                str(status_code), ged_data)
                            logging.error(message)
                            return HttpResponse(status=400, reason=message)
                else:
                    logging.info('passou_aqui_8')
                    # salva o documento baixado no EL como documento relacionado
                    related_document = deepcopy(document)
                    related_document.name = pdf["filename"]
                    related_document.file_kind = DocumentFileKind.PDF_SIGNED.value
                    save_document_data(related_document, has_ged, None, relative_path, document)

            # atualiza o status do documento
            document.status = document_status
            document.save(update_fields=['status'])

            # se o envelope já existe atualiza o status, caso contrário, cria o envelope
            try:
                logging.info('passou_aqui_9')
                envelope = Envelope.objects.get(identifier=envelope_number)
            except Envelope.DoesNotExist:
                logging.info('passou_aqui_10')
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
                logging.info('passou_aqui_11')
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
                        logging.info('passou_aqui_12')
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
                                logging.info('passou_aqui_13')
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
                                logging.info('passou_aqui_14')
                                message = 'Não foi possível salvar o Signer: ' + str(e)
                                logging.info(message)
                                logging.exception(message)
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logging.info('passou_aqui_15')
        logging.error('Exceção webhook clicksign')
        logging.error(message)

    logging.info('passou_aqui_16')
    return HttpResponse(status=200, reason="Success!")


def pdf_file_saver(url, relative_path, document_name):
    # salva o pdf em media/clicksign
    envelope_dir = os.path.join(settings.BASE_DIR, "media", relative_path)
    # cria diretorio e subdiretorio, caso nao exista
    Path(envelope_dir).mkdir(parents=True, exist_ok=True)

    # variável para salvar o nome dos pdfs no signer
    filename_no_extension = str(document_name.split(".pdf")[0])
    filename = filename_no_extension + '-assinado.pdf'
    fullpath = os.path.join(envelope_dir, filename)

    # baixa o pdf no diretorio criado
    urllib.request.urlretrieve(url, fullpath)

    return fullpath, filename
