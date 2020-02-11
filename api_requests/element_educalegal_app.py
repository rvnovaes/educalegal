import coreapi

client = coreapi.Client()


def get_tenant_data(schema, params):
    schema = client.get(schema)
    action = ["tenant", "read"]
    result = client.action(schema, action, params=params)
    # Return one tenants.
    return result


def get_all_schools_data(schema, params):
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    result = client.action(schema, action, params=params)
    # Return all schools from a tenant
    return result


def get_all_schools_names(schema, params):
    schema = client.get(schema)
    action = ["tenant", "school", "list"]
    result = client.action(schema, action, params=params)
    school_names_list = list()
    for school in result:
        school_names_list.append(school['name'])
    return school_names_list
