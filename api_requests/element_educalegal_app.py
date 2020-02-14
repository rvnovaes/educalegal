import coreapi


def create_client(ut):
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=ut)
    client = coreapi.Client(auth=auth)
    return client


def get_tenant_data(ut, schema, params):
    client = create_client(ut)
    schema = client.get(schema)
    action = ["tenant", "read"]
    result = client.action(schema, action, params=params)
    # Return one tenants.
    return result


def get_all_schools_data(ut, schema, params):
    client = create_client(ut)
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    result = client.action(schema, action, params=params)
    # Return all schools from a tenant
    return result


def get_all_schools_names(ut, schema, params):
    client = create_client(ut)
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    result = client.action(schema, action, params=params)
    school_names_list = list()
    for school in result:
        school_names_list.append(school["name"])
    return school_names_list


def get_all_schools_names_data(ut, schema, params):
    client = create_client(ut)
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    all_schools_data = client.action(schema, action, params=params)
    school_names_list = list()
    school_data_dict = dict()
    for school in all_schools_data:
        school_names_list.append(school["name"])
        school_data_dict[school["name"]] = school
    return school_names_list, school_data_dict
