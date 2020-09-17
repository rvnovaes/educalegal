import hashlib
import hmac
import json
import logging

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from api.views_v2 import save_in_ged
from document.models import Document, Envelope, Signer, DocumentStatus, DocumentFileKind
from document.views import save_document_data
from interview.models import Interview
from tenant.models import Tenant, ESignatureAppProvider


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
            logging.error(message)
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
            if envelope_status == "finalizado":
                # ao finalizar as assinaturas do documento estou recebendo um request.body sem a url do pdf assinado
                # resposta do suporte da clicksign: Quando o evento auto_close é disparado pela primeira vez, alguns
                # processos ainda são feitos internamente para que o documento assinado esteja pronto.
                # Dessa forma, é possível que ao receber o primeiro evento, a cópia final ainda não esteja disponível.
                # Sendo assim, recomendamos que a primeira tentativa seja recusada, ou que o evento só seja aceito com
                # URL documento assinado.
                if 'signed_file_url' not in data['document']['downloads']:
                    logging.info('Ignora requisição, pois evento {event} não contém a chave signed_file_url. '
                                 'ID do ocumento {doc_id}'.format(event=data['event']['name'], doc_id=document.id))
                    return HttpResponse(status=400, reason='Falta a chave signed_file_url')

                relative_path = 'docs/' + tenant.name + '/' + document.name[:15] + '/'
                document_url = data['document']['downloads']['signed_file_url']

                # inclui no nome do pdf informacao de assinado
                filename_no_extension = str(document.name.split(".pdf")[0])
                filename = filename_no_extension + '-assinado.pdf'

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
                        # salva documento no ged
                        post_data["label"] = filename
                        status_code, ged_data, ged_id = save_in_ged(post_data, document_url, None, document.tenant)
                    except Exception as e:
                        message = str(e)
                        logging.error(message)
                        return HttpResponse(status=400, reason=message)
                    else:
                        logging.debug("Posting document to GED: " + filename)
                        logging.debug(ged_data)

                        if status_code == 201:
                            # salva o documento baixado no EL como documento relacionado. copia do pai algumas
                            # propriedades
                            related_document = Document(
                                name=filename,
                                description=document.description,
                                interview=document.interview,
                                school=document.school,
                                tenant=document.tenant,
                                bulk_generation=document.bulk_generation,
                                file_kind=DocumentFileKind.PDF_SIGNED.value,
                            )
                            save_document_data(related_document, document_url, None, relative_path, has_ged, ged_data,
                                               filename, document)
                        else:
                            message = 'Não foi possível salvar o documento no GED. {} - {}'.format(
                                str(status_code), ged_data)
                            logging.error(message)
                            return HttpResponse(status=400, reason=message)
                else:
                    # salva o documento baixado no EL como documento relacionado. copia do pai algumas
                    # propriedades
                    related_document = Document(
                        name=filename,
                        description=document.description,
                        interview=document.interview,
                        school=document.school,
                        tenant=document.tenant,
                        bulk_generation=document.bulk_generation,
                        file_kind=DocumentFileKind.PDF_SIGNED.value,
                    )
                    save_document_data(related_document, document_url, None, relative_path, has_ged, None, filename,
                                       document)

            # atualiza o status do documento
            document.status = document_status
            document.save(update_fields=['status'])

            # envia requisicao para webhook
            # sent_document_status_update()

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
                                logging.error(message)
    except Exception as e:
        message = str(type(e).__name__) + " : " + str(e)
        logging.error('Exceção webhook clicksign')
        logging.error(message)

    return HttpResponse(status=200, reason="Success!")
