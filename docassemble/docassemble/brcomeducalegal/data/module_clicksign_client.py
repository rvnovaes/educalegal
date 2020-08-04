import base64

from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

__all__ = ["ClickSignClient", "make_document_base64"]

###### LOCALHOST ######
api_base_url = "https://sandbox.clicksign.com/"
token = "dc0251e3-bb8e-4813-84c0-1158ba0bdbcf"


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

    def upload_document(self, document_name, document_path):
        """
        Envia o documento para o ClickSign.
        :param document_name:
         Nome do arquivo que será criado no ClickSign
        :param document_path:
        Caminho onde o documento será criado dentro da Clicksign, incluindo o nome do arquivo.
        - Campo deverá começar com "/".
        - Se a pastas e as subpastas não existirem, elas serão criadas automaticamente.
        - Esse campo não representa o caminho do seu servidor.
        :return:
        JSON com os dados do documento criado.
        """
        content_base64 = 'data:application/pdf;base64,' + make_document_base64(document_path)

        payload = {
            "document": {
                "path": "/" + document_name,
                "content_base64": content_base64,
                "sequence_enabled": True
                }
            }

        final_url = self.api_base_url + "api/v1/documents"
        response = self.session.post(final_url, json=payload).json()
        return response

    def upload_document2(self, documents):
        for document in documents:
            payload = {
                "document": {
                    "path": "/" + document['name'],
                    "content_base64": document['documentBase64'],
                    "sequence_enabled": True
                    }
                }

        final_url = self.api_base_url + "api/v1/documents"
        response = self.session.post(final_url, json=payload).json()
        return response

    def add_signer(self, recipients):
        """
        Adiciona destinatários para a assinatura eletrônica.
        :param recipients:
         Lista de dicionários com os dados do(s) destinatário(s)
        :return:
        Lista de responses em JSON com os dados do(s) destinatário(s) criado(s).
        """

        response_list = list()
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
            response = self.session.post(final_url, json=payload).json()
            response_list.append(response)

        return response_list

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
        document_response = self.upload_document2(documents)
        signer_response = self.add_signer(recipients)
        signer_to_document_response = self.add_signer_to_document(
            document_response['document']['key'], signer_response)

        return signer_to_document_response


def make_document_base64(document_path):
    """Converts your document from document_path to a base64 string, as used by Docusign"""
    with open(document_path, "rb") as document:
        return base64.b64encode(document.read()).decode("utf-8")


if __name__ == '__main__':
    csc = ClickSignClient(api_base_url, token)

    # print(csc.get_document('9afc2318-4729-4764-810b-ac66c6e6571e'))

    print(csc.send_document('lorem-ipsum.pdf', '/opt/educalegal/api_requests/lorem-ipsum.pdf'))
