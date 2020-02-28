import requests

webhook_url = 'https://app.educalegal.com.br/v1/docusign/webhook'
webhook_url_localhost = 'http://localhost:8000/api/docusign/webhook'
headers = {'Authorization': "Token 	359efadb736eba60f0c705719a28093be699ea3f",
           "Content-Type": "text/xml; charset=UTF-8"}
payload = {"xml": '''
<?xml version="1.0" encoding="UTF-8"?>
'''}

event_notification = {
    "url": webhook_url,
    "loggingEnabled": "true",  # The api wants strings for true/false
    "requireAcknowledgment": "true",
    "useSoapInterface": "false",
    "includeCertificateWithSoap": "false",
    "signMessageWithX509Cert": "false",
    "includeDocuments": "true",
    "includeEnvelopeVoidReason": "true",
    "includeTimeZone": "true",
    "includeSenderAccountAsCustomField": "true",
    "includeDocumentFields": "true",
    "includeCertificateOfCompletion": "true",
    "envelopeEvents": [  # for this recipe, we're requesting notifications
        # for all envelope and recipient events
        {"envelopeEventStatusCode": "sent"},
        {"envelopeEventStatusCode": "delivered"},
        {"envelopeEventStatusCode": "completed"},
        {"envelopeEventStatusCode": "declined"},
        {"envelopeEventStatusCode": "voided"},
    ],
    "recipientEvents": [
        {"recipientEventStatusCode": "Sent"},
        {"recipientEventStatusCode": "Delivered"},
        {"recipientEventStatusCode": "Completed"},
        {"recipientEventStatusCode": "Declined"},
        {"recipientEventStatusCode": "AuthenticationFailed"},
        {"recipientEventStatusCode": "AutoResponded"},
    ],
}


def test_web_hook(url):
    response = requests.post(url, data=payload)
    print(response)


if __name__ == '__main__':
    test_web_hook(webhook_url)
