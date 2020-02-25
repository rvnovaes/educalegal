import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504, 404),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def document_create(url, headers, filename, document_type, label='', language='', description=''):
    file_object = open(filename, mode='rb')
    payload = {'document_type': document_type,
               'label': label,
               'language': language,
               'description': description
    }
    response = requests.post(url, headers=headers, data=payload, files={"file": file_object})
    return response

def document_read(url, headers):
    # response = requests.get(url, headers=headers)
    # return response
    response = requests_retry_session().get(url, headers=headers)
    return response

if __name__ == '__main__':
    url = 'http://localhost:8080/api/documents/'
    tenant_ged_token = 'e12eafe1a884fcce1613f294ac66180efe1b6337'
    token_string = 'Token ' + tenant_ged_token
    headers = {'Authorization': token_string}
    # filename = 'lorem-ipsum.pdf'
    # label = 'lorem_ipsum_teste'
    # response = document_create(url, headers, filename, 2, label, 'por', 'Apenas um teste...' ).json()
    # print(response)
    # document_id =
    document_id = 21
    url = 'http://localhost:8080/api/documents/{id}/'.format(id=document_id)
    response = document_read(url, headers)
    print(response)

