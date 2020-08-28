from requests import Session, RequestException

# https://github.com/bustawin/retry-requests
from retry_requests import retry

from docassemble.base.util import (
    log,
    get_config,
)

__all__ = ["ClickSignClient"]


el_environment = get_config('el environment')
# el_environment = 'production'
# el_environment = 'development'

if el_environment == "production":
    webhook_url = "https://app.educalegal.com.br/v1/clicksign/webhook"
else:
    webhook_url = "https://test.educalegal.com.br/v1/clicksign/webhook"


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
            if el_environment == "production":
                log('Erro ao buscar o documento. Erro: {e}'.format(e=e))
            else:
                log('Erro ao buscar o documento. Erro: {e}'.format(e=e), "console")
            return e
        else:
            return response

    def upload_document(self, document):
        """
        Faz o upload do documento no Clicksign.
        :param document: documento que será enviado para a Clicksign
        :return: JSON com dados do(s) documento(s) adicionado(s)
        """
        payload = {
            "document": {
                "path": "/" + document['name'],
                "content_base64": 'data:application/pdf;base64,' + document['documentBase64'],
                "sequence_enabled": True
                }
            }

        final_url = self.base_url + 'api/v1/documents'

        try:
            response = self.session.post(final_url, json=payload)
        except RequestException:
            if el_environment == "production":
                log('Erro ao fazer o upload do documento. Erro: {status_code} - {response}'.format(
                    status_code=response.status_code, response=response.json()))
            else:
                log('Erro ao fazer o upload do documento. Erro: {status_code} - {response}'.format(
                    status_code=response.status_code, response=response.json()), "console")
            return document, response.json(), response.status_code, ''
        except Exception as e:
            if el_environment == "production":
                log('Erro ao fazer o upload do documento. Erro: {e}'.format(e=e))
            else:
                log('Erro ao fazer o upload do documento. Erro: {e}'.format(e=e), "console")
            return document, e, 0, ''
        else:
            if response.status_code == 201:
                # data_sent, data_received, status_code
                return document, response.json(), response.status_code, response.json()['document']['key']
            else:
                # data_sent, data_received, status_code
                return document, response.json(), response.status_code, response.json()

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
                except RequestException:
                    if el_environment == "production":
                        log('Erro ao adicionar o signatário. Erro: {status_code} - {response}'.format(
                            status_code=response.status_code, response=response.json()))
                    else:
                        log('Erro ao adicionar o signatário. Erro: {status_code} - {response}'.format(
                            status_code=response.status_code, response=response.json()), "console")
                    # data_sent, data_received, status_code
                    return recipients, response.json(), response.status_code
                except Exception as e:
                    if el_environment == "production":
                        log('Erro ao adicionar o signatário. Erro: {e}'.format(e=e))
                    else:
                        log('Erro ao adicionar o signatário. Erro: {e}'.format(e=e), "console")
                    # data_sent, data_received, status_code
                    return recipients, e, 0
                else:
                    recipient['key'] = response.json()['signer']['key']
                    recipient['response_json'] = response.json()
                    recipient['status_code'] = response.status_code

        try:
            # data_sent, data_received, status_code
            return recipients, recipients, response.status_code
        except NameError as e:
            # data_sent, data_received, status_code
            return recipients, recipients, 200

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
            except RequestException:
                if el_environment == "production":
                    log('Erro ao vincular o signatário ao documento. Erro: {status_code} - {response}'.format(
                        status_code=response.status_code, response=response.json()))
                else:
                    log('Erro ao vincular o signatário ao documento. Erro: {status_code} - {response}'.format(
                        status_code=response.status_code, response=response.json()), "console")
                return signers, response.json(), response.status_code
            except Exception as e:
                if el_environment == "production":
                    log('Erro ao vincular o signatário ao documento. Erro: {e}'.format(e=e))
                else:
                    log('Erro ao vincular o signatário ao documento. Erro: {e}'.format(e=e), "console")
                return signers, e, 0
            else:
                if response.status_code == 201:
                    signer['request_signature_key'] = response.json()['list']['request_signature_key']

        try:
            # data_sent, data_received, status_code
            return signers, response.json(), response.status_code
        except NameError as e:
            # data_sent, data_received, status_code
            return signers, 'Signatários já adicionados ao documento', 200

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
                except RequestException:
                    if el_environment == "production":
                        log('Erro ao enviar o email. Erro: {status_code} - {response}'.format(
                            status_code=response.status_code, response=response.reason))
                    else:
                        log('Erro ao enviar o email. Erro: {status_code} - {response}'.format(
                            status_code=response.status_code, response=response.reason), "console")
                    return signature_keys, response.reason, response.status_code
                except Exception as e:
                    if el_environment == "production":
                        log('Erro ao enviar o email. Erro: {e}'.format(e=e))
                    else:
                        log('Erro ao enviar o email. Erro: {e}'.format(e=e), "console")
                    return signature_keys, e, 0

        try:
            # data_sent, data_received, status_code
            return signature_keys, response.reason, response.status_code
        except NameError:
            # data_sent, data_received, status_code
            return signature_keys, 'E-mails enviados', 200

    def send_to_signers(self, doc_uuid, recipients):
        """Cria os destinatários, vincula ao documento e envia por e-mail para assinatura."""

        # data_sent
        data_sent = {'endpoint': 'add_signer_to_document', 'doc_uuid': doc_uuid, 'recipients': recipients}

        # vincula o documento aos destinatarios criados
        recipients, signer_doc_response, status_code = self.add_signer_to_document(doc_uuid, recipients)

        if status_code == 201:
            # envia por email o documento aos destinatarios
            if len(recipients) > 0:
                data_sent, signature_key_response, status_code = self.send_email(recipients)
            else:
                signature_key_response, status_code = 'Não foram encontrados emails para o envio', 0
        else:
            return data_sent, signer_doc_response, status_code

        return data_sent, signature_key_response, status_code
