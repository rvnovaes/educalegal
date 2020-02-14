import requests

url = "http://demo.d4sign.com.br/api/v1/documents/14200bbc-d247-438c-a8e8-de08e7853ff5/upload?tokenAPI=live_ff4719cef73aa88c47761c50b8689be51f60bbbb7be5b7cd7b4c855e36654d1e&cryptKey=live_crypt_fqB9y65rddkyS42pHhiv77PGt35hFtCx"

payload = {}
files = [
  ('file', open('/home/roberto/Área de Trabalho/lorem-ipsum.pdf','rb'))
]
headers = {
  'Content-Type': 'application/pdf'
}

response = requests.request("POST", url, headers=headers, data = payload, files = files)

print(response.text.encode('utf8'))
