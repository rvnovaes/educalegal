from requests import Session, RequestException

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
    webhook_url = "https://app.educalegal.com.br/v1/clicksign/webhook"
else:
    webhook_url = "https://test.educalegal.com.br/v1/clicksign/webhook"


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

        endpoint = 'api/v1/documents'
        final_url = self.base_url + endpoint

        try:
            response = self.session.post(final_url, json=payload)
        except RequestException:
            request_json = {
                "endpoint": endpoint,
                "document": document,
            }
            return response.status_code, response.json(), '', request_json
        except Exception as e:
            request_json = {
                "endpoint": endpoint,
                "document": document,
                "exception": e,
            }
            return 0, None, '', request_json

        return response.status_code, response.json(), response.json()['document']['key'], None

    def add_signer(self, recipients):
        """
        Adiciona destinatários para a assinatura eletrônica.
        :param recipients:
         Lista de dicionários com os dados do(s) destinatário(s)
        :return:
        Lista de responses em JSON com os dados do(s) destinatário(s) criado(s).
        """

        response_dict = dict()
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

            endpoint = 'api/v1/signers'
            final_url = self.base_url + endpoint

            try:
                response = self.session.post(final_url, json=payload)

                if recipient['email'] not in response_dict.keys():
                    response_dict[recipient['email']] = {
                        "response_json": response.json(),
                        "status_code": response.status_code,
                        "routingOrder": recipient['routingOrder']
                    }
            except RequestException:
                request_json = {
                    "endpoint": endpoint,
                    "recipients": recipients,
                    "status_code": response.status_code,
                    "response_json": response.json(),
                }
                if el_environment == "production":
                    log(request_json)
                else:
                    log(request_json, "console")

                return None, request_json
            except Exception as e:
                request_json = {
                    "endpoint": endpoint,
                    "recipients": recipients,
                    "exception": e,
                }
                if el_environment == "production":
                    log(request_json)
                else:
                    log(request_json, "console")

                return None, request_json

        return response_dict, None

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

        response_dict = dict()
        for signer in signers:
            payload = {
                "list": {
                    "document_key": document_uuid,
                    "signer_key": signers[signer]['response_json']['signer']['key'],
                    "sign_as": "sign",
                    "group": signers[signer]['routingOrder'],
                    "message": 'Por favor, assine o documento.'
                },
            }

            endpoint = 'api/v1/lists'
            final_url = self.base_url + endpoint

            try:
                response = self.session.post(final_url, json=payload)

                if signer not in response_dict.keys():
                    response_dict[signer] = {
                        "response_json": response.json(),
                        "status_code": response.status_code,
                        "signer": signers[signer]['response_json']['signer']
                    }
            except RequestException:
                request_json = {
                    "endpoint": endpoint,
                    "document_uuid": document_uuid,
                    "signers": signers,
                    "response_json": response.json(),
                    "status_code": response.status_code,
                }
                if el_environment == "production":
                    log(request_json)
                else:
                    log(request_json, "console")

                return None, request_json
            except Exception as e:
                request_json = {
                    "endpoint": endpoint,
                    "document_uuid": document_uuid,
                    "signers": signers,
                    "exception": e,
                }
                if el_environment == "production":
                    log(request_json)
                else:
                    log(request_json, "console")

                return None, request_json

        return response_dict, None

    def send_email(self, signature_keys):
        """
        Envia o email para os destinatários para a assinatura eletrônica.
        :param signature_keys:
         Lista de signatários para os quais o documento será enviado.
        :return:
        202 - Accepted.
        """

        response_dict = dict()
        for signature_key in signature_keys:
            # envia email somente para os destinatarios do grupo 1 (primeiro na ordem)
            if signature_keys[signature_key]['response_json']['list']['group'] == 1:
                payload = {
                    "request_signature_key": signature_keys[signature_key]['response_json']['list']['request_signature_key'],
                    "message": "Prezado(a) {signer_name},\n\nPor favor, assine o documento.".format(signer_name=signature_keys[signature_key]['signer']['name'])
                }

                endpoint = 'api/v1/notifications'
                final_url = self.base_url + endpoint
        try:
            response = self.session.post(final_url, json=payload)

            if signature_key not in response_dict.keys():
                response_dict[signature_key] = {
                    "status_code": response.status_code,
                    "reason": response.reason
                }
        except RequestException:
            request_json = {
                "endpoint": endpoint,
                "signature_keys": signature_keys,
                "status_code": response.status_code,
                "reason": response.reason
            }
            if el_environment == "production":
                log(request_json)
            else:
                log(request_json, "console")
            return None, request_json
        except Exception as e:
            request_json = {
                "endpoint": endpoint,
                "signature_keys": signature_keys,
                "exception": e,
            }
            if el_environment == "production":
                log(request_json)
            else:
                log(request_json, "console")
            return None, request_json

        return response_dict, None

    def send_to_signers(self, doc_uuid, recipients):
        """Cria os destinatários, vincula ao documento e envia por e-mail para assinatura."""

        # remove os signatarios que nao assinam o documento
        for index, recipient in reversed(list(enumerate(recipients))):
            if recipient['group'] != 'signers':
                del recipients[index]

        # cria os destinatarios
        signer_response, signer_request = self.add_signer(recipients)

        # se nao conseguiu criar algum destinatario, retorna erro
        if signer_response:
            for signer in signer_response:
                if signer_response[signer]['status_code'] != 201:
                    return signer_response[signer]['status_code'], \
                        signer_response[signer]['response_json'], \
                        signer_request
        else:
            return 0, None, signer_request

        # vincula o documento aos destinatarios criados
        signer_doc_response, signer_doc_request = self.add_signer_to_document(doc_uuid, signer_response)

        # se nao vincular algum destinatario ao documento, retorna erro
        if signer_doc_response:
            for signer_doc in signer_doc_response:
                if signer_doc_response[signer_doc]['status_code'] != 201:
                    return signer_doc_response[signer_doc]['status_code'], \
                        signer_doc_response[signer_doc]['response_json'], \
                        signer_doc_request
        else:
            return 0, None, signer_doc_request

        # envia por email o documento aos destinatarios
        signature_key_response, signature_key_request = self.send_email(signer_doc_response)

        # se nao conseguiu enviar o email para algum destinatario, retorna erro
        if signature_key_response:
            log(signature_key_response, "console")
            for signature_key in signature_key_response:
                log(signature_key_response[signature_key]['status_code'], "console")
                if signature_key_response[signature_key]['status_code'] != 202:
                    return signature_key_response[signature_key]['status_code'], \
                        signature_key_response[signature_key]['reason'], \
                        signature_key_request
        else:
            return 0, None, signature_key_request

        return signature_key_response[signature_key]['status_code'], \
            signature_key_response[signature_key]['reason'], None
