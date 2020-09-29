from api.third_party.docusign_client import DocuSignClient

client_id = ""
impersonated_user = ''
private_key = '''-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----'''

dsc = DocuSignClient(client_id, impersonated_user, False, private_key)

envelope_id = 'b01b1b76-8b9e-47bb-806a-7cc32be98d4d'


def list_envelope_attachments():
    status_code, response = dsc.list_envelope_attachments(envelope_id)

    return status_code, response


def get_envelope_attachment():
    status_code, response = dsc.list_envelope_documents(envelope_id)

    if status_code == 200:
        attachments = response['attachments']
        for attachment in attachments:
            status_code, response = dsc.get_envelope_document(envelope_id, attachment['attachmentId'])

    return status_code, response


def download_envelope_document():
    status_code, response = dsc.list_envelope_documents(envelope_id)

    if status_code == 200:
        documents = response['envelopeDocuments']
        for document in documents:
            dsc.download_envelope_document(envelope_id, document['documentId'], document['name'])


if __name__ == '__main__':
    # print(list_envelope_attachments())
    print(download_envelope_document())
