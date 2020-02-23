import sys
import coreapi
from coreapi.exceptions import ErrorMessage

sys.path.append('/opt/docassemble-elements/docassemble/elements/data')

from element_educalegal_app import EducaLegalClient

if __name__ == "__main__":
    ut = "960fc6c3c51349ef0637039c67b09eff497dfa21"
    schema = "http://localhost:8000/v1/docs"
    el_client = EducaLegalClient(ut, schema)
    print(el_client.get_tenant_ged_data(1))
    print(el_client.get_interview_data(2))

    try:
        school_names_list, school_data_dict = el_client.get_all_schools_names_data(1)
        selected_school = "Escola da Lagoa"
        print(school_names_list)
        print(school_data_dict)
        for school_name in school_names_list:
            print(school_name)
        for school_data in school_data_dict:
            try:
                selected_school_data = school_data_dict[selected_school]
                print(selected_school_data)
            except KeyError:
                pass
    except ErrorMessage as e:
        print(e)
