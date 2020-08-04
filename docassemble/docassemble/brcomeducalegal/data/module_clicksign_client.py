import json

from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

__all__ = ["ClickSignClient"]


class ClickSignClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
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
        final_url = self.api_base_url + "api/v1/documents/{uuid}".format(uuid=uuid)
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

        final_url = self.api_base_url + "api/v1/documents"
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

            final_url = self.api_base_url + "api/v1/signers"
            response = self.session.post(final_url, json=payload)

            if recipient['email'] not in response_dict.keys():
                response_dict[recipient['email']] = {
                    "response_json": response.json(),
                    "status_code": response.status_code
                }

        response_dict = json.dumps(response_dict)

        return response_dict

    def add_signer_to_document(self, document_uuid, signers):
        """
        Adiciona no documento os destinatários para a assinatura eletrônica.
        :param document_uuid:
         Identificador único do documento
        :return:
        JSON com os dados do documento vinculado ao signatário.
        """

        for signer in signers:
            payload = {
                "list": {
                    "document_key": "/" + document_uuid,
                    "signer_key": signer['key'],
                    "sign_as": "sign",
                    "group": signer['routingOrder'],
                    "message": 'Assine eletrônicamente esse documento.'
                },
            }

        final_url = self.api_base_url + "api/v1/lists"
        response = self.session.post(final_url, json=payload).json()
        return response

    def send_to_cliksign(self, documents, recipients):
        status_code, document_response = self.upload_document2(documents)

        if status_code == 200:
            status_code, signer_response = self.add_signer(recipients)

        status_code, signer_to_document_response = self.add_signer_to_document(
            document_response['document']['key'], signer_response)

        return signer_to_document_response
