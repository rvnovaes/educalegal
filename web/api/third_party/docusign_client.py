# DocuSign Integration for Docassemble
import logging
import json
import jwt
import re
import requests
import time

from base64 import b64encode
from os import path

__all__ = ["DocuSignClient", "make_document_base64"]

logger = logging.getLogger(__name__)

RECIPIENT_TYPES = {
    "agents": {},
    "carbonCopies": {},
    "certifiedDeliveries": {},
    "editors": {},
    "inPersonSigners": {},
    "intermediaries": {},
    "seals": {},
    "signers": {},
}

TAB_TYPES = {
    "approve": {"abbreviation": "appro", "set_value": False},
    "checkbox": {"abbreviation": "check", "set_value": True},
    "company": {"abbreviation": "compa", "set_value": False},
    "dateSigned": {"abbreviation": "dates", "set_value": False},
    "date": {"abbreviation": "datex", "set_value": True},
    "decline": {"abbreviation": "decli", "set_value": False},
    "email": {"abbreviation": "email", "set_value": True},
    "envelopeId": {"abbreviation": "envel", "set_value": False},
    "firstName": {"abbreviation": "first", "set_value": False},
    "formulaTab": {"abbreviation": "formu", "set_value": True},
    "fullName": {"abbreviation": "fulln", "set_value": False},
    "initialHere": {"abbreviation": "initi", "set_value": False},
    "lastName": {"abbreviation": "lastn", "set_value": False},
    "list": {"abbreviation": "list", "set_value": True},
    "notarize": {"abbreviation": "notar", "set_value": True},
    "note": {"abbreviation": "note", "set_value": True},
    "number": {"abbreviation": "numbe", "set_value": True},
    "radioGroup": {"abbreviation": "radio", "set_value": True},
    "signHere": {"abbreviation": "signh", "set_value": False},
    "signerAttachment": {"abbreviation": "signe", "set_value": False},
    "ssn": {"abbreviation": "ssn", "set_value": True},
    "text": {"abbreviation": "text", "set_value": True},
    "title": {"abbreviation": "title", "set_value": False},
    "view": {"abbreviation": "view", "set_value": True},
    "zip": {"abbreviation": "zip", "set_value": True},
}


class DocuSignClient:
    def __init__(self, client_id, impersonated_user_guide, test_mode, private_key, *pargs, **kwargs):
        # Parameters
        # auth_only indicates that the interview is creating the object for authorization only,
        # and so it will not check for any configuration data beyond client_id and test_mode.

        self.client_id = client_id
        self.impersonated_user_guid = impersonated_user_guide
        self.test_mode = test_mode
        self.private_key = private_key

        if self.test_mode:
            webhook_url = "https://api-test.educalegal.com.br/v1/docusign/webhook"
        else:
            webhook_url = "https://api-app.educalegal.com.br/v1/docusign/webhook"

        if self.test_mode:
            self.aud = "account-d.docusign.com"
            self.base_uri = "https://account-d.docusign.com"
        else:
            self.aud = "account.docusign.com"
            self.base_uri = "https://account.docusign.com"

        self.get_token()
        self.get_user_info()

        self.event_notification = {
            "url": webhook_url,
            "loggingEnabled": "true",  # The api wants strings for true/false
            "requireAcknowledgment": "true",
            "useSoapInterface": "false",
            "includeCertificateWithSoap": "false",
            "signMessageWithX509Cert": "false",
            "includeDocuments": "true",
            "includeEnvelopeVoidReason": "true",
            "includeTimeZone": "true",
            "includeSenderAccountAsCustomField": "true",
            "includeDocumentFields": "true",
            "includeCertificateOfCompletion": "true",
            "envelopeEvents": [  # for this recipe, we're requesting notifications
                # for all envelope and recipient events
                {"envelopeEventStatusCode": "sent"},
                {"envelopeEventStatusCode": "delivered"},
                {"envelopeEventStatusCode": "completed"},
                {"envelopeEventStatusCode": "declined"},
                {"envelopeEventStatusCode": "voided"},
            ],
            "recipientEvents": [
                {"recipientEventStatusCode": "Sent"},
                {"recipientEventStatusCode": "Delivered"},
                {"recipientEventStatusCode": "Completed"},
                {"recipientEventStatusCode": "Declined"},
                {"recipientEventStatusCode": "AuthenticationFailed"},
                {"recipientEventStatusCode": "AutoResponded"},
            ],
        }

    def authorization_link(self):
        if self.test_mode:
            base_url = "https://account-d.docusign.com/oauth/auth"
        else:
            base_url = "https://account.docusign.com/oauth/auth"
        url = (
            base_url + "?response_type=code&scope=signature%20impersonation&client_id="
        )
        url += self.client_id

        return url

    def get_token(self):
        current_time = int(time.time())
        hour_later = int(time.time()) + 3600
        self.jwt_code = jwt.encode(
            {
                "iss": self.client_id,
                "sub": self.impersonated_user_guid,
                "iat": current_time,
                "exp": hour_later,
                "aud": self.aud,
                "scope": "signature impersonation",
            },
            self.private_key,
            algorithm="RS256",
        )
        request_for_token = requests.post(
            self.base_uri + "/oauth/token",
            data={
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": self.jwt_code,
            },
        )
        self.token = json.loads(request_for_token.text)["access_token"]


    def get_user_info(self):
        self.authorization_header = {"Authorization": "Bearer " + self.token}
        request_for_user = requests.get(
            self.base_uri + "/oauth/userinfo", headers=self.authorization_header
        )
        user_account_id = json.loads(request_for_user.text)["accounts"][0]["account_id"]
        user_base_uri = json.loads(request_for_user.text)["accounts"][0]["base_uri"]
        self.extended_base_uri = (
            user_base_uri + "/restapi/v2/accounts/" + user_account_id
        )

    def test_api_connection(self):
        # This function just tests whether authentication works well enough to obtain the user's
        # specific server and account ID, as required in the last step of JWT authentication.
        # If it outputs '/restapi/v2/accounts/' authentication is not working.
        # If it outputs 'https://server.address/restapi/v2/accounts/client-id' then it is working.

        return self.extended_base_uri

    def send_to_docusign(
        self,
        recipients,
        documents,
        custom_fields=[],
        email_subject="Please Sign",
        assign_doc_ids=True,
        assign_recipient_ids=True,
        assign_field_ids=True,
        **kwargs
    ):
        """Creates an envelope and prepares it to be sent to a number of recipients."""
        # Check received recipients are okay whilst rotating the format to fix Docusign API
        rotated_recipients = {}
        message = ''
        for index, recipient in enumerate(recipients):
            if "name" not in recipient.keys():
                message = "Falta a chave 'name' nos destinatários."
            if "email" not in recipient.keys():
                message = "Falta a chave 'email' nos destinatários."
            if "routingOrder" not in recipient.keys():
                message = "Falta a chave 'routingOrder' nos destinatários."
            else:
                if not re.match(
                    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                    recipient["email"],
                ):
                    message = "Email formatado incorretamente."
            if assign_recipient_ids:
                recipient["recipientId"] = index + 1
            elif "recipientId" not in recipient.keys():
                message = (
                    "Falta a chave 'recipientId' nos destinatários."
                )
            if "tabs" in recipient.keys():
                rotated_tabs = {}
                for tab in recipient["tabs"]:
                    if "type" not in tab.keys():
                        message = "Falta a chave 'type' na tab."
                    tab_type = tab["type"]
                    tab_type_extended = tab_type + "Tabs"
                    del tab["type"]
                    if tab_type not in TAB_TYPES.keys():
                        message = "Tipo de tab inválida."
                    if not TAB_TYPES[tab_type]["set_value"]:
                        if not all(
                            key not in tab.keys() for key in ["locked", "originalValue"]
                        ):
                            message = "Valor não pode ser controlado para esse tipo de tab."
                    if tab_type_extended not in rotated_tabs.keys():
                        rotated_tabs[tab_type_extended] = [tab]
                    else:
                        rotated_tabs[tab_type_extended].append(tab)
                del recipient["tabs"]
                recipient["tabs"] = rotated_tabs
            if "group" not in recipient.keys():
                message = "Falta a chave 'group' nos destinatários."
            recipient_group = recipient["group"]
            del recipient["group"]
            if recipient_group not in rotated_recipients.keys():
                rotated_recipients[recipient_group] = [recipient]
            else:
                rotated_recipients[recipient_group].append(recipient)

        # Check received documents are okay whilst assigning ids if asked to
        for index, document in enumerate(documents):
            if "name" not in document.keys():
                message = "Falta a chave 'name' no documento."
            if "fileExtension" not in document.keys():
                message = "Falta a chave 'fileExtension' no documento."
            if assign_doc_ids:
                document["documentId"] = index + 1
            elif "documentId" not in document.keys():
                message = "Falta a chave 'documentId' no documento."
            if "documentBase64" not in document.keys():
                message = "Falta a chave 'documentBase64' no documento."

        # Check received envelope custom fields and rotate format
        rotated_fields = {"listCustomFields": [], "textCustomFields": []}
        for index, field in enumerate(custom_fields):
            if assign_field_ids:
                field["fieldId"] = index + 1
            elif "fieldId" not in field.keys():
                message = "Missing 'fieldId' no campo."
            if "type" not in field.keys():
                message = "Falta a chave 'type' no campo customizado."
            if field["type"] == "list":
                del field["type"]
                rotated_fields["listCustomFields"].append(field)
            elif field["type"] == "text":
                del field["type"]
                rotated_fields["textCustomFields"].append(field)
            else:
                message = "Campo customizado inválido."
        if message:
            message = 'Não foi possível enviar para a assinatura eletrônica. Motivo: ' + message
            return message

        # Build our request json
        request_json = {
            "status": "sent",
            "emailSubject": email_subject,
            "recipients": rotated_recipients,
            "documents": documents,
            "envelopecustomFields": rotated_fields,
            "eventNotification": self.event_notification,
        }

        for key in kwargs:
            request_json[key] = kwargs[key]

        try:
            envelope = requests.post(
                self.extended_base_uri + "/envelopes",
                headers=self.authorization_header,
                json=request_json,
            )
            envelope.raise_for_status()
            return envelope.status_code, json.loads(envelope.text)
        except Exception as e:
            message = str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return 0, message

    def list_envelope_documents(self, envelope_id):
        """Retorna a lista de documentos do envelope"""

        try:
            envelope_documents = requests.get(
                self.extended_base_uri + "/envelopes/" + envelope_id + '/documents', headers=self.authorization_header
            )
        except Exception as e:
            message = str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return 0, message
        else:
            return envelope_documents.status_code, envelope_documents.json()

    def get_envelope_document(self, envelope_id, document_id):
        """Retorna a URL do documento"""

        try:
            envelope_document = requests.get(
                self.extended_base_uri + "/envelopes/" + envelope_id + '/documents/' + document_id,
                headers=self.authorization_header
            )
        except Exception as e:
            message = str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return 400, message
        else:
            if envelope_document.status_code == 200:
                return envelope_document.status_code, envelope_document
            else:
                return envelope_document.status_code, envelope_document.json()['message']

    def download_envelope_document(self, envelope_id, document_id, filepath, filename):
        """Baixa o documento no diretório indicado"""

        try:
            status_code, document = self.get_envelope_document(envelope_id, document_id)
        except Exception as e:
            message = str(type(e).__name__) + " : " + str(e)
            logger.error(message)
            return 400, message
        else:
            if status_code == 200:
                try:
                    with open(path.join(filepath, filename), 'wb') as f:
                        f.write(document.content)
                except Exception as e:
                    message = str(type(e).__name__) + " : " + str(e)
                    logger.error(message)
                    return 400, message

            if isinstance(document, str):
                return status_code, document
            else:
                return status_code, document.reason


def make_document_base64(document):
    """Converts your document from document_path to a base64 string, as used by Docusign"""
    return b64encode(document.read()).decode("utf-8")
