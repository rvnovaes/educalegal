from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

from docassemble.base.util import (
    log,
    get_config,
    url_of,
)

__all__ = ["ClickSignClient"]

el_environment = get_config('el environment')
# el_environment = 'development'

if el_environment == "production":
    webhook_url = "https://app.educalegal.com.br/v1/docusign/webhook"
else:
    webhook_url = "https://test.educalegal.com.br/v1/docusign/webhook"


class ClickSignClient:
    def __init__(self, token, test_mode):
        self.test_mode = test_mode
        self.token = token
        self.target_uri = url_of("interview", _external=True)

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
        response = self.session.get(final_url).json()
        return response

    def upload_document(self, documents):
        for document in documents:
            payload = {
                "document": {
                    "path": "/" + document['name'],
                    "content_base64": 'data:application/pdf;base64,' + document['documentBase64'],
                    "sequence_enabled": True
                    }
                }

        final_url = self.base_url + "api/v1/documents"
        response = self.session.post(final_url, json=payload)
        return response.status_code, response.json()

    def add_signer(self, recipients):
        """
        Adiciona destinatários para a assinatura eletrônica.
        :param recipients:
         Lista de dicionários com os dados do(s) destinatário(s)
        :return:
        Lista de responses em JSON com os dados do(s) destinatário(s) criado(s).
        """

        response_dict = dict()
        recipients = recipients['signers']
        for recipient in recipients:
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

            final_url = self.base_url + "api/v1/signers"
            response = self.session.post(final_url, json=payload)

            if recipient['email'] not in response_dict.keys():
                response_dict[recipient['email']] = {
                    "response_json": response.json(),
                    "status_code": response.status_code,
                    "routingOrder": recipient['routingOrder']
                }

        return response_dict

    def add_signer_to_document(self, document_uuid, signers):
        """
        Adiciona no documento os destinatários para a assinatura eletrônica.
        :param document_uuid:
         Identificador único do documento
        :return:
        JSON com os dados do documento vinculado ao signatário.
        """

        response_dict = dict()
        for signer in signers:
            payload = {
                "list": {
                    "document_key": document_uuid,
                    "signer_key": signers[signer]['response_json']['signer']['key'],
                    "sign_as": "sign",
                    "group": signers[signer]['routingOrder'],
                    "message": 'Por favor assine o documento.'
                },
            }

            final_url = self.base_url + "api/v1/lists"
            response = self.session.post(final_url, json=payload)

            if signer not in response_dict.keys():
                response_dict[signer] = {
                    "response_json": response.json(),
                    "status_code": response.status_code,
                    "signer": signers[signer]['response_json']['signer']
                }

        return response_dict

    def send_email(self, signature_keys):
        """
        Adiciona no documento os destinatários para a assinatura eletrônica.
        :param document_uuid:
         Identificador único do documento
        :return:
        JSON com os dados do documento vinculado ao signatário.
        """

        response_dict = dict()
        for signature_key in signature_keys:
            # envia email somente para os destinatarios do grupo 1 (primeiro na ordem)
            if signature_keys[signature_key]['response_json']['list']['group'] == 1:
                payload = {
                    "request_signature_key": signature_keys[signature_key]['response_json']['list']['request_signature_key'],
                    "message": "Prezado(a) {signer_name},\n\nPor favor, assine o documento.".format(signer_name=signature_keys[signature_key]['signer']['name'])
                }

                final_url = self.base_url + "api/v1/notifications"
                response = self.session.post(final_url, json=payload)

                if signature_key not in response_dict.keys():
                    response_dict[signature_key] = {
                        "status_code": response.status_code,
                        "reason": response.reason
                    }

        return response_dict

    def send_to_clicksign(self, documents, recipients):
        # cria o documento
        status_code, document_response = self.upload_document(documents)

        # se nao conseguiu criar o documento, retorna erro
        if status_code != 201:
            return status_code, document_response

        # cria os destinatarios
        signer_response = self.add_signer(recipients)

        for signer in signer_response:
            # se nao conseguiu criar algum destinatario, retorna erro
            if signer_response[signer]['status_code'] != 201:
                return signer_response[signer]['status_code'], signer_response[signer]['response_json']

        # vincula o documento aos destinatarios criados
        signer_doc_response = self.add_signer_to_document(
            document_response['document']['key'], signer_response)

        for signer_doc in signer_doc_response:
            # se nao vincular algum destinatario ao documento, retorna erro
            if signer_doc_response[signer_doc]['status_code'] != 201:
                return signer_doc_response[signer_doc]['status_code'], signer_doc_response[signer_doc]['response_json']

        # envia por email o documento aos destinatarios
        signature_key_response = self.send_email(signer_doc_response)

        for signature_key in signature_key_response:
            # se nao conseguiu enviar o email para algum destinatario, retorna erro
            if signature_key_response[signature_key]['status_code'] != 202:
                return signature_key_response[signature_key]['status_code'], signature_key_response[signature_key]['reason']

        return signature_key_response[signature_key]['status_code'], signature_key_response[signature_key]['reason']
