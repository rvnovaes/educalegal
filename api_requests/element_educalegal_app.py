import coreapi

def get_tenant_data(schema, params):
    # Initialize a client & load the schema document
    client = coreapi.Client()
    schema = client.get(schema)

    # Interact with the API endpoint
    action = ["tenant", "read"]
    result = client.action(schema, action, params=params)
    # Return list of tenants. As we consulted by uuid, it will always return only one
    return result[0]