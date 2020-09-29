from api.third_party.mayan_client import MayanClient

# https://ged-educalegal.educalegal.com.br (Educa Legal)
# base_url = 'https://ged-educalegal.educalegal.com.br'
# tenant_ged_token = 'aaa4d93a7611637578984d43958eedc6316e42f3'
=========
sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from element_mayan_client import MayanClient
>>>>>>>>> Temporary merge branch 2

# https://gedtest.educalegal.com.br (Development)
# base_url = 'https://gedtest.educalegal.com.br'
# tenant_ged_token = '5bbf160ccb0d02c7da908a7fea5301bdd07f132e'

# https://127.0.0.1:8000 (localhost)
base_url = 'http://ged:8000'
tenant_ged_token = '483473d37efb328b827c354471be6e082236a2d9'

# iasmini
# tenant_ged_token = '3feed0201f22b2d89fe3a714f6106f6820415320'

mc = MayanClient(base_url, tenant_ged_token)


def create_document():
    filename = '20200916-060329-termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.pdf'
    document_type = 1
    label = "aaaa20200916-060329-termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.pdf"
    language = "por"
    description = "teste | teste | 2020-05-26"

    return mc.document_create(filename, document_type, label, language, description)


if __name__ == '__main__':
    print(create_document())
    # document_id = 1958
    # response = mc.document_read(document_id)
    # print(response)
    # response = mc.document_download(document_id)
    # print(response)



