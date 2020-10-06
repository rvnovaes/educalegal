import requests
endpoint = "https://apitest.educalegal.com.br/v2/documents/?page=1"
resposta = requests.get(endpoint, headers={'Authorization': 'Token 4a7e0551374e00bdcf3e333f5570618bf6d77778'})
print(resposta.text)
