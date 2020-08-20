import sys
from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry
import time
from requests.exceptions import RequestException

import sys

sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from element_mayan_client import MayanClient

# https://ged-educalegal.educalegal.com.br (Educa Legal)
base_url = 'https://ged-educalegal.educalegal.com.br'
tenant_ged_token = 'aaa4d93a7611637578984d43958eedc6316e42f3'

# https://gedtest.educalegal.com.br (Development)
# base_url = 'https://gedtest.educalegal.com.br'
# tenant_ged_token = '5bbf160ccb0d02c7da908a7fea5301bdd07f132e'

if __name__ == '__main__':
    mc = MayanClient(base_url, tenant_ged_token)
    # filename = 'lorem-ipsum.pdf'
    # label = 'lorem_ipsum_teste'
    # response = mc.document_create(filename, 1, label, 'por', 'Apenas um teste...').json()
    # print(response)
    # document_id = 1958
    # response = mc.document_read(document_id)
    # print(response)
    # response = mc.document_download(document_id)
    # print(response)

    # apaga os documentos no mayan
    response = mc.document_bulk_delete(5787, 10000)
    print(response)
