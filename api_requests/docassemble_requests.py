import requests

educa_legal_url = 'http://localhost:8000/api/tenant'


response = requests.get(educa_legal_url)
print(response.content)