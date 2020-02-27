import sys

sys.path.append("/opt/docassemble-elements/docassemble/elements/data")
from element_educalegal_client import EducaLegalClient

if __name__ == "__main__":
    # api_base_url_localhost = "http://localhost:8000"
    # token_localhost = "914c485c0f1b7ac35097474ac9932c34a3b16783"
    api_base_url_docs_silex = "https://app.educalegal.com.br"
    token_docs_silex = "83c0867e920cab1977d6dd0384f95e2508e6b9d4"

    el = EducaLegalClient(api_base_url_docs_silex, token_docs_silex)
    print(el.tenants_ged_read(2))
    print(el.tenants_esignature_read(2))
    print(el.tenants_schools_list(2))
    print(el.tenants_schools_names(2))
    print(el.tenants_school_names_school_data(2))
    print(el.interviews_read(2))

    # name = "20200255_033504_contrato_de_prestacao_de_servicos_educacionais.pdf"
    # status = "criado"
    # envelope_id = None
    # signing_provider = None
    # ged_id = 1
    # ged_link = "http://whatever"
    # ged_uuid = "179dad8b-99b0-494a-8f81-257d3705029d"
    # description = "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23"
    # tenant = 2
    # school = 1
    # interview = 2
    # related_documents = None

    # response = el.create_document(
    #     name,
    #     status,
    #     envelope_id,
    #     signing_provider,
    #     ged_id,
    #     ged_link,
    #     ged_uuid,
    #     description,
    #     tenant,
    #     school,
    #     interview,
    #     related_documents,
    # )
    # print(response)

    # new_status = 'sent'
    # new_envelope_id = '035322ff-6acc-4c1d-992d-a6a68ca6b68a'
    # new_signing_provider = 'Docusign'
    # response = el.patch_document(ged_id, new_status, new_envelope_id, new_signing_provider)
    # print(response)
