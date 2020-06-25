import sys
from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry
import time
from requests.exceptions import RequestException

sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from element_mayan_client import MayanClient

base_url = 'http://localhost:8080'
tenant_ged_token = '483473d37efb328b827c354471be6e082236a2d9'

if __name__ == '__main__':
    mc = MayanClient(base_url, tenant_ged_token)
    # filename = 'lorem-ipsum.pdf'
    # label = 'lorem_ipsum_teste'
    # response = mc.document_create(filename, 1, label, 'por', 'Apenas um teste...').json()
    # print(response)
    document_id = 23
    response = mc.document_read(document_id)
    print(response)

