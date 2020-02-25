from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry


class MayanClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=0.5,
            status_to_retry=(500, 502, 504, 404),
        )
        self.session.headers.update(headers)

    def document_create(self, filename, document_type, label='', language='', description=''):
        file_object = open(filename, mode='rb')
        payload = {'document_type': document_type,
                   'label': label,
                   'language': language,
                   'description': description
        }
        final_url = self.api_base_url + "/api/documents/"
        response = self.session.post(final_url, data=payload, files={"file": file_object})
        return response

    def document_read(self, document_id):
        final_url = self.api_base_url + "/api/documents/{id}".format(id=document_id)
        response = self.session.get(final_url).json()
        return response


if __name__ == '__main__':
    base_url = 'http://localhost:8080'
    tenant_ged_token = 'e12eafe1a884fcce1613f294ac66180efe1b6337'
    mc = MayanClient(base_url, tenant_ged_token)
    filename = 'lorem-ipsum.pdf'
    label = 'lorem_ipsum_teste'
    response = mc.document_create(filename, 2, label, 'por', 'Apenas um teste...').json()
    print(response)
    document_id = 21
    response = mc.document_read(document_id)
    print(response)

