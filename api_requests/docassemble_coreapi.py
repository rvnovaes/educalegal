import coreapi
from coreapi.exceptions import ErrorMessage


class EducaLegalClient:
    def __init__(self, user_token, schema):
        self.client = coreapi.Client(
            auth=coreapi.auth.TokenAuthentication(scheme="Token", token=user_token)
        )
        self.schema = self.client.get(schema)

    def get_tenant_data(self, tid):
        params = {"id": tid}
        action = ["tenant", "ged", "read"]
        result = self.client.action(self.schema, action, params=params)
        # Return one tenant.
        return result

    def get_all_schools_data(self, tid):
        params = {"id": tid}
        action = ["tenant", "school", "list"]
        result = self.client.action(self.schema, action, params=params)
        # Return all schools from a tenant
        return result

    def get_all_schools_names(self, tid):
        params = {"id": tid}
        action = ["tenant", "school", "list"]
        result = self.client.action(self.schema, action, params=params)
        school_names_list = list()
        for school in result:
            school_names_list.append(school["name"])
        return school_names_list

    def get_all_schools_names_data(self, tid):
        params = {"id": tid}
        action = ["tenant", "school", "list"]
        all_schools_data = self.client.action(self.schema, action, params=params)
        school_names_list = list()
        school_data_dict = dict()
        for school in all_schools_data:
            school_names_list.append(school["name"])
            school_data_dict[school["name"]] = school
        return school_names_list, school_data_dict


if __name__ == "__main__":
    ut = "a80f958d2a484f756c4b738d04a6179c1b8a7676"
    schema = "http://localhost:8000/api/docs"
    el_client = EducaLegalClient(ut, schema)
    print(el_client.get_tenant_data(1))

    try:
        school_names_list, school_data_dict = el_client.get_all_schools_names_data(
            params
        )
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
