import sys

sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from element_mayan_client import MayanClient

base_url = 'http://ged:8000'
tenant_ged_token = '483473d37efb328b827c354471be6e082236a2d9'

# base_url = 'https://gedtest.educalegal.com.br'
# tenant_ged_token = '5bbf160ccb0d02c7da908a7fea5301bdd07f132e'

# iasmini
# tenant_ged_token = '47f210da48587cb14357e4352d31e0a9c3ae63c0'

mc = MayanClient(base_url, tenant_ged_token)


def create_document():
    filename = '20200916-060329-termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.pdf'
    document_type = 1
    label = "aaaa20200916-060329-termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.pdf"
    language = "por"
    description = "teste | teste | 2020-05-26"

    # response = mc.document_create(filename, document_type, label, language, description)

    return mc.document_create_message_docid(filename, document_type, label, language, description)


if __name__ == '__main__':
    print(create_document())
    # document_id = 1958
    # response = mc.document_read(document_id)
    # print(response)
    # response = mc.document_download(document_id)
    # print(response)



