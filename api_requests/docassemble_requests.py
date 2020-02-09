import requests

educa_legal_url = 'http://localhost:8000/api/tenant/'
tenant_uuid = '615c182b-42b1-4ea8-9f71-855990f923d0'

response = requests.get(educa_legal_url + tenant_uuid).json()
url_ged = response[0]['ged_url']
# print(response)
