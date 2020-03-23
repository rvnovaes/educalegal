import sys

sys.path.append("/opt/docassemble-brcomeducalegal/docassemble/brcomeducalegal/data")
from element_educalegal_client import EducaLegalClient

###### LOCALHOST ######
# api_base_url = "http://localhost:8000"
# token = "2d5918c936f65be81dfdf6f587f3e6d53d63eb3a"
##### app.educalegal.com.br #####
api_base_url = "https://app.educalegal.com.br"
token = "dbc67c03a50a11f974276fdb08a5820ecda6249b"


if __name__ == "__main__":

    elc = EducaLegalClient(api_base_url, token)
    # print(elc.tenants_ged_read(2))
    # print(elc.tenants_esignature_read(2))
    # print(elc.tenants_schools_list(2))
    # print(elc.tenants_schools_names(2))
    school_names_list, school_units_dict, school_data_dict =  elc.tenants_school_names_school_data(2)
    print(school_names_list)
    print(school_units_dict)
    print(school_names_list, school_units_dict, school_data_dict)
    # print(elc.interviews_read(2))

    # name = "20200229_666666_contrato_de_prestacao_de_servicos_educacionais.pdf"
    # status = "criado"
    # envelope_id = None
    # signing_provider = None
    # ged_id = 1
    # ged_link = "http://whatever"
    # ged_uuid = "179dad8b-9bg6-4945-8f81-257d37050111"
    # description = "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23"
    # tenant = 1
    # school = 1
    # interview = 2
    # related_documents = None
    #
    # response = elc.create_document(
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
