import sys
from requests import Session
# https://github.com/bustawin/retry-requests
from retry_requests import retry
import time
from requests.exceptions import RequestException

import sys

# sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from api.third_party.mayan_client import MayanClient

# https://ged-educalegal.educalegal.com.br (Educa Legal)
# base_url = 'https://ged-educalegal.educalegal.com.br'
# tenant_ged_token = 'aaa4d93a7611637578984d43958eedc6316e42f3'

# https://gedtest.educalegal.com.br (Development)
# base_url = 'https://gedtest.educalegal.com.br'
# tenant_ged_token = '5bbf160ccb0d02c7da908a7fea5301bdd07f132e'
base_url = 'http://ged:8000'
tenant_ged_token = '483473d37efb328b827c354471be6e082236a2d9'
# iasmini
# tenant_ged_token = '3feed0201f22b2d89fe3a714f6106f6820415320'

# https://127.0.0.1:8000 (localhost)
base_url = 'http://ged:8000'
tenant_ged_token = '3feed0201f22b2d89fe3a714f6106f6820415320'

if __name__ == '__main__':
    mc = MayanClient(base_url, tenant_ged_token)
    # filename = 'lorem-ipsum.pdf'
    # data = {
    #     "description": 'Apenas um teste...',
    #     "document_type": 1,
    #     "label": 'lorem_ipsum_teste',
    #     "language": 'por',
    # }
    # response = mc.document_create(data, filename).json()
    # print(response)
    # document_id = 1958
    # response = mc.document_read(document_id)
    # print(response)
    # response = mc.document_download(document_id)
    # print(response)

    # apaga os documentos no mayan - 6209
    response = mc.document_type_read(1)
    print(response)
