import pandas as pd

from datetime import datetime
from os import path
from pathlib import Path

from api.third_party.docusign_client import DocuSignClient


client_id = ""
impersonated_user = ''
private_key = '''-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----'''


def download_docusign_files():
    filename = 'bahema_docusign.csv'
    # envelope_id = 'b01b1b76-8b9e-47bb-806a-7cc32be98d4d'
    envelope_list = pd.read_csv(filename).to_dict(orient='records')

    dsc = DocuSignClient(client_id, impersonated_user, False, private_key)

    log_file = open("log.txt", "w")

    print(datetime.now())

    for index, envelope in enumerate(envelope_list):
        print(str(index) + ' de ' + str(len(envelope_list)))

        if envelope['status'] != 'Completed':
            continue

        status_code, response = dsc.list_envelope_documents(envelope['envelope_id'])

        filepath = path.join('/tmp/bahema', envelope['school'])

        # cria diretorio e subdiretorio, caso nao exista
        Path(filepath).mkdir(parents=True, exist_ok=True)

        if status_code == 200:
            documents = response['envelopeDocuments']
            filename_no_extension = None
            for document in documents:
                if status_code == 200:
                    if document['type'] == 'content':
                        filename_no_extension = document['name'].split(".pdf")[0]
                        document['name'] = filename_no_extension + '-assinado.pdf'
                    else:
                        if filename_no_extension:
                            document['name'] = str(filename_no_extension) + '-certificado.pdf'
                        else:
                            document['name'] = 'certificado.pdf'
                    try:
                        status_code, response = dsc.download_envelope_document(
                            envelope['envelope_id'], document['documentId'], filepath, document['name'])
                    except Exception as e:
                        message = str(type(e).__name__) + " : " + str(e)
                        status_code = 400
                        print(envelope['envelope_id'] + ' - ' + message)
                        break

        if status_code != 200:
            print(envelope['envelope_id'] + ' - ' + response['errorCode'] + ' - ' + response['message'])
            break

        # imprime log com arquivos nao baixados
        log_file.write(str(envelope['envelope_id']) + ' - ' + str(status_code) + '\n')

    log_file.close()
    print(datetime.now())


if __name__ == "__main__":
    download_docusign_files()
