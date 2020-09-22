from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

# from docassemble.base.util import log


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

    def document_types_list(self):
        final_url = self.api_base_url + "/v2/interviews/document_types/"
        response = self.session.get(final_url).json()
        return response

    def document_types_names_list(self):
        document_types_list = self.document_types_list()
        document_types_names_list = list()
        for document_types in document_types_list:
            document_types_names_dict = dict()
            document_types_names_dict[document_types["id"]] = document_types["name"]
            document_types_names_list.append(document_types_names_dict)
        return document_types_names_list

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
        school_witnesses_dict = dict()
        for school in schools_list:
            school_names_list.append(school["name"])
            school_data_dict[school["name"]] = school
            school_units_dict[school["name"]] = school["school_units"]
            school_witnesses_dict[school["name"]] = school["witnesses"]
        return school_names_list, school_units_dict, school_data_dict, school_witnesses_dict

    def witnesses_list(self, school_id):
        final_url = self.api_base_url + "/v2/schools/{id}/witnesses/".format(id=school_id)
        response = self.session.get(final_url).json()
        return response

    def patch_document(self, data, params):
        final_url = self.api_base_url + "/v2/documents/{}".format(params['doc_uuid'])

        try:
            response = self.session.patch(final_url, data=data, params=params)
        except Exception as e:
            # log("e", "console")
            # log(e, "console")
            return None, str(e)
        else:
            return response.status_code, response.json()
