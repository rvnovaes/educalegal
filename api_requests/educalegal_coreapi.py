import sys
import coreapi
from coreapi.exceptions import ErrorMessage

sys.path.append('/opt/docassemble-elements/docassemble/elements/data')



from element_educalegal_app import EducaLegalClient

if __name__ == "__main__":
    ut = "32c7ff84169e1aa7f33e1dc23abb72b394fc53dc"
    schema = "http://localhost:8000/v1/docs"
    el_client = EducaLegalClient(ut, schema)
    # try:
    #     school_names_list, school_data_dict = el_client.get_all_schools_names_data(1)
    #     selected_school = "Escola da Lagoa"
    #     print(school_names_list)
    #     print(school_data_dict)
    #     for school_name in school_names_list:
    #         print(school_name)
    #     for school_data in school_data_dict:
    #         try:
    #             selected_school_data = school_data_dict[selected_school]
    #             print(selected_school_data)
    #         except KeyError:
    #             pass
    # except ErrorMessage as e:
    #     print(e)
    # print(el_client.get_tenant_ged_data(1))
    # print(el_client.get_interview_data(2))
    # print(el_client.get_tenant_esignature_data(2))
    print(el_client.create_document(
        "20200255_033504_contrato_de_prestacao_de_servicos_educacionais.pdf",
        "sent",
        "035322ff-6acc-4c1d-992d-a6a68ca6b68a",
        "Docusign",
        "Empty",
        "179dad8b-99b0-494a-8f81-257d3705029d ",
        "Contrato de prestação de serviços educacionais entre aluno e escola. - 1.1 - 2020-01-23",
        2,
        1,
        2,
        None,))


