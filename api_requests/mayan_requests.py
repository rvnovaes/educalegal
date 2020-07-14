import sys
from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry
import time
from requests.exceptions import RequestException

from element_mayan_client import MayanClient

base_url = 'http://ged:8000'
tenant_ged_token = '483473d37efb328b827c354471be6e082236a2d9'

if __name__ == '__main__':
    mc = MayanClient(base_url, tenant_ged_token)
    # filename = 'lorem-ipsum.pdf'
    # label = 'lorem_ipsum_teste'
    # response = mc.document_create(filename, 1, label, 'por', 'Apenas um teste...').json()
    # print(response)
    document_id = 1958
    response = mc.document_read(document_id)
    print(response)
    response = mc.document_download(document_id)
    print(response)



