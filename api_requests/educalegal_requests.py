import sys

sys.path.append("/opt/educalegal/docassemble/docassemble/brcomeducalegal/data")
from element_educalegal_client import EducaLegalClient
from module_clicksign_client import ClickSignClient

###### LOCALHOST ######
token_csc = "dc0251e3-bb8e-4813-84c0-1158ba0bdbcf"

csc = ClickSignClient(token_csc, True)

###### LOCALHOST ######
api_base_url = "http://localhost:8001"
token = "9fa535d8bcfb4ce6410a59d46c61368334c96ddc"
##### app.educalegal.com.br #####
# api_base_url = "https://app.educalegal.com.br"
# token = "dbc67c03a50a11f974276fdb08a5820ecda6249b"


if __name__ == "__main__":
    elc = EducaLegalClient(api_base_url, token)

    # # Dados do Tenant
    # print(elc.tenants_read(2))
    #
    # # Dados do GED do Tenant
    # print(elc.tenants_ged_read(2))
    #
    # # Dados das Escolas de um Tenant
    # print(elc.tenants_schools_list(2))
    #
    # # Nomes das Escolas de um Tenant
    # print(elc.tenants_schools_names(2))
    #
    # # Nomes das Escolas de um Tenant, Nomes das Unidades de uma Escola, Dicionario de dados das Esolas
    # (
    #     school_names_list,
    #     school_units_dict,
    #     school_data_dict,
    # ) = elc.tenants_school_names_school_data(2)
    # print(school_names_list)
    # print(school_units_dict)
    # print(school_names_list, school_units_dict, school_data_dict)
    #
    # # Dados da Entrevista
    # print(elc.interviews_read(3))
    #
    # # Criação de documento
    # # name = "20200229_666666_contrato_de_prestacao_de_servicos_educacionais.pdf"
    # name = "---"
    # # status = "criado"
    # status = "rascunho"
    # envelope_number = None
    # # ged_id = 1
    # # ged_link = "http://whatever"
    # # ged_uuid = "179dad8b-9bg6-4945-8f81-257d37050111"
    # description = "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23"
    # tenant = 2
    # school = 2
    # interview = 82
    # # related_documents = None
    # # document_data = "test"
    #
    # response = elc.create_document(
    #     name,
    #     status,
    #     description,
    #     tenant,
    #     interview,
    #     school,
    #     # related_documents,
    #     # document_data,
    # )
    # el_document_created_id = response["id"]
    # el_document_created_doc_uuid = response["doc_uuid"]
    # print(el_document_created_id)
    #
    # # Atualizacao de documento com dados do GED (Depende do valor para a ID do documento criado no método anterior
    # ged_id = 1
    # ged_link = "ged_link"
    # ged_uuid = "010101010101"
    #
    # response = elc.patch_document_with_email_data(
    #     el_document_created_doc_uuid, send_email=True, status="enviado por e-mail"
    # )
    # print(response)
    #
    # response = elc.patch_document_with_ged_data(
    #     el_document_created_doc_uuid, ged_id, ged_link, ged_uuid, status="inserido no GED",
    # )
    #
    # print(response)
    #
    # # Atualização de documento com dos de ESignature (Depende do valor para ID do documento criado no método anterior)
    #
    # ged_id = 1
    # new_status = "modificado"
    # new_envelope_number = '3fc59949-23ab-4301-b4ce-1176f1246954'
    # response = elc.patch_document_with_esignature_data(
    #     el_document_created_doc_uuid, new_status, new_envelope_number, submit_to_esignature=False
    # )
    # print(response)

    # =========== elc.post_envelope ============= #
    # tid = 1
    # data_received = {
    #   "envelopeId": "aaa",
    #   "status": "sent",
    #   "statusDateTime": "2020-07-30T16:49:23.7938569Z",
    #   "uri": "/envelopes/b08b6022-fbb9-4e47-955f-eda4ac3f13a0"
    # }
    # esignature_provider = 'Docusign'
    #
    # response, status_code = elc.post_envelope(tid, esignature_provider, data_received)
    #
    # print(status_code)
    #
    # print(response)
    # =========== elc.post_envelope ============= #


    # =========== elc.post_signers ============= #
    # el_recipients = [
    #     {'name': 'Ut est sed sed ipsa', 'email': 'dogoka@mailinator.com', 'group': 'signers', 'status': 'gerado',
    #      'sent_date': '', 'tenant': '1', 'envelope_log': 27,
    #      'pdf_filenames': '20200717-112740-termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.pdf'},
    #     {'name': 'Development Sociedade de Ensino Colégio Bacana Ltda.', 'email': 'silex@silexsistemas.com.br',
    #      'group': 'signers', 'status': 'gerado', 'sent_date': '', 'tenant': '1', 'envelope_log': 27,
    #      'pdf_filenames': '20200717-112740-termo-de-acordo-individual-de-banco-de-horas-mp-927-2020.pdf'}
    # ]
    #
    # documents = {'name': 'documento.pdf'}
    # tid = 1
    # envelope_log_response = dict()
    # envelope_log_response['id'] = 27
    #
    # el_post_signers_log, status_code = elc.post_signers_log(el_recipients, documents, tid, envelope_log_response['id'])
    #
    # print(status_code)
    #
    # print(el_post_signers_log)
    # =========== elc.post_signers ============= #


    # =========== elc.get_signer_key_by_email ============= #
    recipients = [
        {
            'name': 'Development Sociedade de Ensino Colégio Bacana Ltda.',
            'email': 'silex@silexsistemas.com.br',
            'group': 'signers',
            'routingOrder': 1,
            'tabs': [
                {
                    'type': 'signHere',
                    'anchorString': 125973285101946
                }
            ]
        },
        {
            'name': 'IASMINI FURTADO DE MAGALHAES GOMES',
            'email': 'iasmini.gomes@gmail.com',
            'group': 'certifiedDeliveries',
            'routingOrder': 2
        },
        {
            'name': 'Contato Financeiro',
            'email': 'financeiro2@silexsistemas.com.br',
            'group': 'carbonCopies',
            'routingOrder': 3
        }
    ]

    status_code, recipients = elc.get_signer_key_by_email(recipients)

    # cria os destinatarios
    recipients_sign, data_sent = csc.add_signer(recipients)

    # =========== elc.get_signer_key_by_email ============= #
