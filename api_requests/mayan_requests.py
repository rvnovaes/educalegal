from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry
import time
from requests.exceptions import RequestException



class MayanClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=0.5,
            status_to_retry=(500, 502, 504)
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
        number_of_tries = 3
        try:
            for i in range(number_of_tries):
                t = 0.5 * pow(2, (i - 1))
                response = self.session.get(final_url)
                if response.status_code == 404 and i < number_of_tries - 1:
                    print(t)
                    time.sleep(t)
                elif response.status_code == 404 and i == number_of_tries - 1:
                    error_message = (
                        "<h5>O documento não foi criado no GED!</h5>"
                        "<b>Status Code :</b> {status_code}<br>"
                        "<b>Reason :</b> {reason}<br>"
                        "<b>URL do GED:</b> {url}<br><br>"
                    ).format(
                        status_code=str(response.status_code),
                        reason=response.reason,
                        url=response.url,
                    )
                    return error_message
                else:
                    return response.json()
        except RequestException as e:
            error_message = (
                "<h5>O documento não foi criado no GED!</h5><br>"
                "<b>Exception:</b> {e}<br><br>"
            ).format(e=str(e))
            return error_message


if __name__ == '__main__':
    base_url = 'http://localhost:8080'
    tenant_ged_token = '483473d37efb328b827c354471be6e082236a2d9'
    mc = MayanClient(base_url, tenant_ged_token)
    # filename = 'lorem-ipsum.pdf'
    # label = 'lorem_ipsum_teste'
    # response = mc.document_create(filename, 1, label, 'por', 'Apenas um teste...').json()
    # print(response)
    document_id = 23
    response = mc.document_read(document_id)
    print(response)

