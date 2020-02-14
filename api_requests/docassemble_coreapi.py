import coreapi


auth = coreapi.auth.TokenAuthentication(
    scheme="Token",
    token="6511907b374c6475c16c17d35795d1b36804005c"
)
client = coreapi.Client(auth=auth)

def get_tenant_data(schema, params):
    schema = client.get(schema)
    action = ["tenant", "read"]
    result = client.action(schema, action, params=params)
    # Return one tenant
    return result


def get_all_schools_data(schema, params):
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    result = client.action(schema, action, params=params)
    # Return all schools from a tenant
    return result


def get_all_schools_names_data(schema, params):
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    all_schools_data = client.action(schema, action, params=params)
    school_names_list = list()
    school_data_dict = dict()
    for school in all_schools_data:
        school_names_list.append(school['name'])
        school_data_dict[school['name']] = school
    return school_names_list, school_data_dict


if __name__ == "__main__":
    schema = "http://localhost:8000/api/docs"
    params = {"id": 1}
    # result = get_tenant_data(schema, params)
    # result = get_all_schools_data(schema, params)
    school_names_list, school_data_dict = get_all_schools_names_data(schema, params)
    selected_school = 'Escola da Lagoa'
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
