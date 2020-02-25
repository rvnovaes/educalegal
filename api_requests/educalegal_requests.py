from requests import Session
#https://github.com/bustawin/retry-requests
from retry_requests import retry


class EducaLegalClient:

    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(Session(), retries=3, backoff_factor=0.5, status_to_retry=(500, 502, 504, 404))
        self.session.headers.update(headers)

    def tenants_ged_read(self, tid):
        final_url = self.api_base_url + "/v1/tenants/{id}/ged/".format(id=tid)
        response = self.session.get(final_url).json()
        return response

    def tenants_esignature_read(self, tid):
        final_url = self.api_base_url + "/v1/tenants/{id}/esignature/".format(id=tid)
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
        for school in schools_list:
            school_names_list.append(school["name"])
            school_data_dict[school["name"]] = school
        return school_names_list, school_data_dict

    def interviews_read(self, intid):
        final_url = self.api_base_url + "/v1/interviews/{id}".format(id=intid)
        response = self.session.get(final_url).json()
        return response

    def create_document(
            self,
            name,
            status,
            envelope_id,
            signing_provider,
            ged_link,
            ged_uuid,
            description,
            tenant,
            school,
            interview,
            related_documents,
    ):
        payload = {
            "name": name,
            "status": status,
            "envelope_id": envelope_id,
            "signing_provider": signing_provider,
            "ged_link": ged_link,
            "ged_uuid": ged_uuid,
            "description": description,
            "tenant": tenant,
            "school": school,
            "interview": interview,
            "related_documents": related_documents,
        }
        final_url = self.api_base_url + "/v1/documents/"
        response = self.session.post(final_url, data=payload)
        return response



if __name__ == "__main__":
    api_base_url = 'http://localhost:8000'
    token = "311648a5e598e7d60b3e7f982909a34a0214f1f4"
    el = EducaLegalClient(api_base_url, token)
    print(el.tenants_ged_read(2))
    print(el.tenants_esignature_read(2))
    print(el.tenants_schools_list(2))
    print(el.tenants_schools_names(2))
    print(el.tenants_school_names_school_data(2))
    print(el.interviews_read(2))
    print(el.create_document(
        "20200255_033504_contrato_de_prestacao_de_servicos_educacionais.pdf",
        "sent",
        "035322ff-6acc-4c1d-992d-a6a68ca6b68a",
        "Docusign",
        "Empty",
        "179dad8b-99b0-494a-8f81-257d3705029d ",
        "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23",
        2,
        1,
        2,
        None,))



