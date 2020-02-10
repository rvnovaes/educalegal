import coreapi


def get_tenant_data(schema, params):
    # Initialize a client & load the schema document
    client = coreapi.Client()
    schema = client.get(schema)

    # Interact with the API endpoint
    action = ["tenant", "read"]
    result = client.action(schema, action, params=params)
    # Return list of tenants. As we consulted by uuid, it will always return only one
    return result


def get_school_data(schema, params):
    # Initialize a client & load the schema document
    client = coreapi.Client()
    schema = client.get(schema)

    # Interact with the API endpoint
    action = ["school", "read"]
    result = client.action(schema, action, params=params)
    # Return list of tenants. As we consulted by uuid, it will always return only one
    return result


if __name__ == "__main__":
    schema = "http://localhost:8000/api/docs"
    params = {"id": 1}
    result = get_tenant_data(schema, params)
    # result = get_school_data(schema, params)
    print(result)
