import coreapi

# Initialize a client & load the schema document
client = coreapi.Client()
schema = client.get("http://localhost:8000/api/docs")

# Interact with the API endpoint
action = ["tenant", "read"]
params = {
    "unique_id": "a8c8ceb8-6717-4007-b894-5dd9f7e7b793",
}
result = client.action(schema, action, params=params)
print(result[0]['name'])