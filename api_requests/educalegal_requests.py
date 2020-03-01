import sys

sys.path.append("/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data")
from element_educalegal_client import EducaLegalClient

if __name__ == "__main__":
    api_base_url_localhost = "http://localhost:8000"
    token_localhost = "2b2d1a0eae6a1fac3b87ba8496e654174255b9d5"
    # api_base_url_docs_silex = "https://app.educalegal.com.br"
    # token_docs_silex = "83c0867e920cab1977d6dd0384f95e2508e6b9d4"

    elc = EducaLegalClient(api_base_url_localhost, token_localhost)
    # print(el.tenants_ged_read(2))
    # print(el.tenants_esignature_read(2))
    # print(el.tenants_schools_list(2))
    # print(el.tenants_schools_names(2))
    # print(el.tenants_school_names_school_data(2))
    # print(el.interviews_read(2))

    name = "20200229_666666_contrato_de_prestacao_de_servicos_educacionais.pdf"
    status = "criado"
    envelope_id = None
    signing_provider = None
    ged_id = 1
    ged_link = "http://whatever"
    ged_uuid = "179dad8b-9bg6-4945-8f81-257d37050111"
    description = "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23"
    tenant = 1
    school = 1
    interview = 2
    related_documents = None

    response = elc.create_document(
        name,
        status,
        envelope_id,
        signing_provider,
        ged_id,
        ged_link,
        ged_uuid,
        description,
        tenant,
        school,
        interview,
        related_documents,
    )
    print(response)

    # Representa a modificação 17 elc.create_document pela primeira vez

    # ged_id = 1
    # new_status = 'modificado'
    # new_envelope_id = '035322ff-6acc-4c1d-992d-a6a68ca6b68a'
    # new_signing_provider = 'Docusign'
    # response = elc.patch_document(ged_id, new_status, new_envelope_id, new_signing_provider)
    # print(response)

    # ged_id = None
    # status = 'assinado2'
    # envelope_id = '035322ff-6acc-4c1d-992d-a6a68ca6b68a'
    # signing_provider = 'Docusign'
    # esignature_log = "LOG enviado pelo Docusign"
    # response = elc.patch_document(ged_id, status, envelope_id, signing_provider, esignature_log)
