import json
from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

from document.models import DocumentStatus


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
        status=DocumentStatus.INSERIDO_GED,
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
        status=DocumentStatus.ENVIADO_EMAIL,
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
