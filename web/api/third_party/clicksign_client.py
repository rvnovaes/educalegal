import logging
import os

from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry

logger = logging.getLogger(__name__)

__all__ = ["ClickSignClient"]


class ClickSignClient:
    def __init__(self, token, test_mode):
        self.test_mode = test_mode
        self.token = token

        if self.test_mode:
            self.base_url = "https://sandbox.clicksign.com/"
        else:
            self.base_url = "https://app.clicksign.com/"

        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=1,
            status_to_retry=(500, 502, 504),
        )
        # o token deve ser passado como parametro e não no header
        params = {'access_token': token}
        self.session.params.update(params)

    def get_document(self, uuid):
        final_url = self.base_url + "api/v1/documents/{uuid}".format(uuid=uuid)
        try:
            response = self.session.get(final_url).json()
        except Exception as e:
            message = 'Erro ao buscar o documento. Erro: {e}'.format(e=e)
            logger.error(message)
            return message
        else:
            return response

    def upload_document(self, document):
        """
        Faz o upload do documento no Clicksign.
        :param document: documento que será enviado para a Clicksign
        :return: JSON com dados do(s) documento(s) adicionado(s)
        """
        path = os.path.join("/", document["tenant"]["esignature_folder"], document["school"]["esignature_folder"],
                            document['name'])

        payload = {
            "document": {
                "path": path,
                "content_base64": 'data:application/pdf;base64,' + document['documentBase64'],
                "sequence_enabled": True
                }
            }

        final_url = self.base_url + 'api/v1/documents'

        try:
            response = self.session.post(final_url, json=payload)
        except Exception as e:
            message = 'Erro ao fazer o upload do documento. Erro: {e}'.format(e=e)
            logger.error(message)
            return 500, message, 0
        else:
            if response.status_code == 201:
                return response.status_code, response.json(), response.json()['document']['key']
            else:
                message = 'Erro ao fazer o upload do documento. Erro: {status_code} - {response}'.format(
                    status_code=response.status_code, response=response.json())
                logger.error(message)
                return response.status_code, response.json(), 0

    def add_signer(self, recipients):
        """
        Adiciona destinatários para a assinatura eletrônica.
        :param recipients:
         Lista de dicionários com os dados do(s) destinatário(s)
        :return:
        Lista de responses em JSON com os dados do(s) destinatário(s) criado(s).
        """

        for recipient in recipients:
            if 'key' not in recipient:
                recipient['key'] == ''
                recipient['status_code'] == '404'

            if recipient['key'] == '':
                payload = {
                    "signer": {
                        "email": recipient['email'],
                        "auths": [
                            "email"
                        ],
                        "name": recipient['name'],
                        "has_documentation": False,
                        "delivery": "email"
                    }
                }

                final_url = self.base_url + 'api/v1/signers'

                try:
                    response = self.session.post(final_url, json=payload)
                except Exception as e:
                    message = 'Erro ao adicionar o signatário. Erro: {e}'.format(e=e)
                    logger.error(message)
                    return 500, message
                else:
                    if response.status_code == 201:
                        recipient['key'] = response.json()['signer']['key']
                        recipient['response_json'] = response.json()
                        recipient['status_code'] = response.status_code
                    else:
                        message = 'Erro ao adicionar o signatário {name} - {email}.'.format(
                            name=recipient['name'], email=recipient['email'])
                        if 'errors' in response.json():
                            message += ' Erro: {status_code} - {response}'.format(
                                       status_code=response.status_code,
                                       response=response.json()['errors'])
                            return response.status_code, message
                        else:
                            message += ' Erro: {status_code} - {response}'.format(
                                       status_code=response.status_code,
                                       response=response.json())
                            return response.status_code, message

                        logger.error(message)
        try:
            return response.status_code, response.json()
        except NameError:
            return 201, 'Destinatários já existem.'

    def add_signer_to_document(self, document_uuid, signers):
        """
        Adiciona no documento os destinatários para a assinatura eletrônica.
        :param document_uuid:
         Identificador único do documento
        :param signers:
         Lista de signatários que será adicionada ao documento
        :return:
        JSON com os dados do documento vinculado ao signatário.
        """

        for signer in signers:
            payload = {
                "list": {
                    "document_key": document_uuid,
                    "signer_key": signer['key'],
                    "sign_as": signer['group'],
                    "group": signer['routingOrder'],
                    "message": 'Por favor, assine o documento.'
                },
            }

            final_url = self.base_url + 'api/v1/lists'

            try:
                response = self.session.post(final_url, json=payload)
            except Exception as e:
                message = 'Erro ao vincular o signatário ao documento. Erro: {e}'.format(e=e)
                logger.error(message)
                return 500, message
            else:
                if response.status_code == 201:
                    signer['request_signature_key'] = response.json()['list']['request_signature_key']
                else:
                    message = 'Erro ao vincular o signatário ao documento. Erro: {status_code} - {response}'.format(
                        status_code=response.status_code, response=response.json())
                    logger.error(message)

        try:
            return response.status_code, response.json()
        except NameError as e:
            return 200, 'Signatários já adicionados ao documento'

    def send_email(self, signature_keys):
        """
        Envia o email para os destinatários para a assinatura eletrônica.
        :param signature_keys:
         Lista de signatários para os quais o documento será enviado.
        :return:
        202 - Accepted.
        """

        for signature_key in signature_keys:
            # envia email somente para os destinatarios do grupo 1 (primeiro na ordem)
            if signature_key['routingOrder'] == 1:
                payload = {
                    "request_signature_key": signature_key['request_signature_key'],
                    "message": "Prezado(a) {signer_name},\n\nPor favor, assine o documento.".format(
                        signer_name=signature_key['name'])
                }

                final_url = self.base_url + 'api/v1/notifications'

                try:
                    response = self.session.post(final_url, json=payload)
                except Exception as e:
                    message = 'Erro ao enviar o email. Erro: {e}'.format(e=e)
                    logger.error(message)
                    return 500, message
                else:
                    if response.status_code != 202:
                        message = 'Erro ao enviar o email. Erro: {status_code} - {response}'.format(
                            status_code=response.status_code, response=response.reason)
                        logger.error(message)

        try:
            #  data_received, status_code
            return response.status_code, response.reason
        except NameError:
            #  data_received, status_code
            return 200, 'E-mails enviados'

    def send_to_signers(self, doc_uuid, recipients):
        """Cria os destinatários, vincula ao documento e envia por e-mail para assinatura."""

        # vincula o documento aos destinatarios criados
        status_code, signer_doc_response = self.add_signer_to_document(doc_uuid, recipients)

        if status_code == 201:
            # envia por email o documento aos destinatarios
            if len(recipients) > 0:
               status_code, signature_key_response = self.send_email(recipients)
            else:
                status_code, signature_key_response = 0, 'Não foram encontrados emails para o envio'
        else:
            return status_code, signer_doc_response

        return status_code, signature_key_response
