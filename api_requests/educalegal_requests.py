import sys
import json

sys.path.append("/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data")
from element_educalegal_client import EducaLegalClient

###### LOCALHOST ######
api_base_url = "http://localhost:8008"
token = "48974bcc7b577ab3d6fed7c281d90324f4612810"
##### app.educalegal.com.br #####
# api_base_url = "https://app.educalegal.com.br"
# token = "dbc67c03a50a11f974276fdb08a5820ecda6249b"


if __name__ == "__main__":

    elc = EducaLegalClient(api_base_url, token)
    # Dados do Tenant
    print(elc.tenants_read(2))

    # Dados do GED do Tenant
    print(elc.tenants_ged_read(2))

    # Dados de ESignature do Tenant
    print(elc.tenants_esignature_read(2))

    # Dados das Escolas de um Tenant
    print(elc.tenants_schools_list(2))

    # Nomes das Escolas de um Tenant
    print(elc.tenants_schools_names(2))

    # Nomes das Escolas de um Tenant, Nomes das Unidades de uma Escola, Dicionario de dados das Esolas
    (
        school_names_list,
        school_units_dict,
        school_data_dict,
    ) = elc.tenants_school_names_school_data(2)
    print(school_names_list)
    print(school_units_dict)
    print(school_names_list, school_units_dict, school_data_dict)

    # Dados da Entrevista
    print(elc.interviews_read(3))

    # Criação de documento
    # name = "20200229_666666_contrato_de_prestacao_de_servicos_educacionais.pdf"
    name = "---"
    # status = "criado"
    status = "rascunho"
    envelope_id = None
    signing_provider = None
    # ged_id = 1
    # ged_link = "http://whatever"
    # ged_uuid = "179dad8b-9bg6-4945-8f81-257d37050111"
    description = "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23"
    tenant = 2
    # school = 1
    interview = 83
    # related_documents = None
    # document_data = "test"


    response = elc.create_document(
        name,
        status,
        description,
        tenant,
        # school,
        interview,
        # related_documents,
        # document_data,
    )
    el_document_created_id = response["id"]
    print(el_document_created_id)

    # Atualizacao de documento com dados do GED (Depende do valor para a ID do documento criado no método anterior
    ged_id = 1
    ged_link = "ged_link"
    ged_uuid = "010101010101"

    response = elc.patch_document_with_ged_data(
        el_document_created_id, ged_id, ged_link, ged_uuid, status="Inserido no GED",
    )

    print(response)

    # Atualização de documento com dos de ESignature (Depende do valor para ID do documento criado no método anterior)

    ged_id = 1
    new_status = "modificado"
    new_envelope_id = "035322ff-6acc-4c1d-992d-a6a68ca6b68a"
    new_signing_provider = "Docusign"
    response = elc.patch_document_with_esignature_data(
        el_document_created_id, new_status, new_envelope_id, new_signing_provider
    )
    print(response)