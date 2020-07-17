import json

from docassemble.base.util import log
from enum import Enum
from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

envelope_statuses = {'sent': 'enviado para assinatura',
                     'delivered': 'enviado para assinatura',
                     'completed': 'assinado',
                     'declined': 'assinatura recusada/inválida',
                     'voided': 'assinatura recusada/inválida'}

recipient_group_types_dict = {
    "agents": "agent",
    "carbonCopies": "carboncopy",
    "certifiedDeliveries": "certifieddelivery",
    "editors": "editor",
    "inPersonSigners": "inpersonsigner",
    "intermediaries": "intermediary",
    "seals": "seal",
    "signers": "signer",
    "witness": "witness"
}


class DocumentStatus(Enum):
    RASCUNHO = "rascunho"
    CRIADO = "criado"
    INSERIDO_GED = "inserido no GED"
    ENVIADO_EMAIL = "enviado por e-mail"
    ENVIADO_ASS_ELET = "enviado para assinatura"
    ASSINADO = "assinado"
    RECUSADO_INVALIDO = "assinatura recusada/inválida"
    NAO_ENCONTRADO = "não encontrado"


class EducaLegalClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=1,
            status_to_retry=(500, 502, 504),
        )
        self.session.headers.update(headers)

    def interviews_read(self, intid):
        final_url = self.api_base_url + "/v1/interviews/{id}".format(id=intid)
        response = self.session.get(final_url).json()
        return response

    def plans_read(self, plan_id):
        final_url = self.api_base_url + "/v1/plans/{id}".format(id=plan_id)
        response = self.session.get(final_url).json()
        return response

    def tenants_read(self, tid):
        final_url = self.api_base_url + "/v1/tenants/{id}".format(id=tid)
        response = self.session.get(final_url).json()
        return response

    def tenants_ged_read(self, tid):
        final_url = self.api_base_url + "/v1/tenants/{id}/ged/".format(id=tid)
        response = self.session.get(final_url).json()
        return response

    def tenants_schools_list(self, tid):
        final_url = self.api_base_url + "/v1/tenants/{id}/schools/".format(id=tid)
        response = self.session.get(final_url).json()
        return response

    def tenants_schools_names(self, tid):
        schools_list = self.tenants_schools_list(tid)
        school_names_list = list()
        for school in schools_list:
            school_names_list.append(school["name"])
        return school_names_list

    def tenants_school_names_school_data(self, tid):
        schools_list = self.tenants_schools_list(tid)
        school_names_list = list()
        school_data_dict = dict()
        school_units_dict = dict()
        for school in schools_list:
            school_names_list.append(school["name"])
            school_data_dict[school["name"]] = school
            school_units_dict[school["name"]] = school["school_units"]
        return school_names_list, school_units_dict, school_data_dict

    def create_document(
        self,
        name,
        status,
        description,
        tenant,
        interview,
        school=None,
        related_documents=None,
        document_data=None,
    ):

        payload = {
            "name": name,
            "status": status,
            "description": description,
            "tenant": tenant,
            "school": school,
            "interview": interview,
            "related_documents": related_documents,
            "document_data": json.dumps(document_data),
        }
        final_url = self.api_base_url + "/v1/documents/"
        response = self.session.post(final_url, data=payload)
        return response.json()

    def patch_document_with_docassemble_data(
        self,
        doc_uuid,
        name,
        description,
        status,
        school,
        related_documents,
        document_data
    ):
        payload = {
            "doc_uuid": doc_uuid,
            "name": name,
            "description": description,
            "status": status,
            "school": school,
            "related_documents": related_documents,
            "document_data": json.dumps(document_data)
        }

        final_url = self.api_base_url + "/v1/documents/"
        response = self.session.patch(final_url, data=payload)
        return response.json()

    def patch_document_with_ged_data(
        self,
        doc_uuid,
        ged_id,
        ged_link,
        ged_uuid,
        status=DocumentStatus.INSERIDO_GED.value,
    ):

        payload = {
            "doc_uuid": doc_uuid,
            "ged_id": ged_id,
            "ged_link": ged_link,
            "ged_uuid": ged_uuid,
            "status": status,
        }
        final_url = self.api_base_url + "/v1/documents/"
        response = self.session.patch(final_url, data=payload)
        return response.json()

    def patch_document_with_email_data(
        self,
        doc_uuid,
        send_email,
        status=DocumentStatus.ENVIADO_EMAIL.value,
    ):

        payload = {
            "doc_uuid": doc_uuid,
            "send_email": send_email,
            "status": status,
        }
        final_url = self.api_base_url + "/v1/documents/"
        response = self.session.patch(final_url, data=payload)
        return response.json()

    def patch_document_with_esignature_data(
        self,
        doc_uuid,
        status,
        envelope_id,
        signing_provider,
        submit_to_esignature,
        related_documents=None
    ):

        if related_documents is None:
            related_documents = []

        # traduz o status
        if status in envelope_statuses.keys():
            status = envelope_statuses[status]
        else:
            status = 'não encontrado'

        payload = {
            "doc_uuid": doc_uuid,
            "status": status,
            "envelope_id": envelope_id,
            "signing_provider": signing_provider,
            "submit_to_esignature": submit_to_esignature,
            "related_documents": related_documents
        }
        final_url = self.api_base_url + "/v1/documents/"
        response = self.session.patch(final_url, data=payload)
        return response.json()

    def post_envelope_log(self, tenant_id, doc_uuid, data_received):
        """Cria registro com o log do envio do email para cada assinante"""

        # formato da data usado no django rest framework: YYYY-MM-DDThh:mm[:ss[.uuuuuu]]
        payload = {
            "envelope_id": data_received['envelopeId'],
            "status": "enviado",
            "envelope_created_date": data_received['statusDateTime'][:26],
            "sent_date": data_received['statusDateTime'][:26],
            'status_update_date': '',
            "tenant": tenant_id,
        }
        final_url = self.api_base_url + "/v1/documents/{uuid}/envelope_logs/".format(uuid=doc_uuid)

        try:
            response = self.session.post(final_url, data=payload)
        except Exception as e:
            log("Erro ao gravar o envelope_log", "console")
            log(e, "console")

        return response.json(), response.status_code

    def post_signers_log(self, tenant_id, recipients, documents, envelope_log_id):
        """Cria registro com o log do envio do email para cada assinante"""

        for recipient in recipients:
            if recipient['email']:
                pdf_filenames = ''
                for index, document in enumerate(documents):
                    if index > 0:
                        pdf_filenames += ' | ' + document['name']
                    else:
                        pdf_filenames = document['name']

                try:
                    payload = {
                        "name": recipient['name'],
                        "email": recipient['email'],
                        "type": recipient_group_types_dict[recipient['group']],
                        "status": 'enviado para assinatura',
                        "sent_date": '',
                        "pdf_filenames": pdf_filenames,
                        "tenant": tenant_id,
                        "envelope_log": envelope_log_id,
                    }
                    final_url = self.api_base_url + "/v1/envelope_logs/{id}/signer_logs/".format(id=envelope_log_id)
                except Exception as e:
                    log("Erro ao gerar o payload do signers_log", "console")
                    log(e, "console")

        try:
            response = self.session.post(final_url, data=payload)
        except Exception as e:
            log("Erro ao gravar o signers_log", "console")
            log(e, "console")
        return response.json(), response.status_code

