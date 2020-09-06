import requests

webhook_url = 'https://app.educalegal.com.br/v1/docusign/webhook'
webhook_url_localhost = 'http://localhost:8000/api/docusign/webhook'
headers = {'Authorization': "Token 	359efadb736eba60f0c705719a28093be699ea3f",
           "Content-Type": "text/xml; charset=UTF-8"}
payload = {"xml": '''
<?xml version="1.0" encoding="UTF-8"?>
'''}


def test_web_hook(url):
    response = requests.post(url, data=payload)
    print(response)


if __name__ == '__main__':
    test_web_hook(webhook_url)
