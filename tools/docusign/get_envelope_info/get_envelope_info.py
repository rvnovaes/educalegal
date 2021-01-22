import pandas as pd

from datetime import datetime

from api.third_party.docusign_client import DocuSignClient

# pegar dados da docusign para acesso à api
client_id = ""
impersonated_user = 'get_envelope_info'
private_key = '''-----BEGIN RSA PRIVATE KEY-----
-----END RSA PRIVATE KEY-----'''


def get_envelope_info():
    """Lê os envelopes do csv, busca os respectivos dados na Docusign e loga o status"""
    filename = 'docusign.csv'
    # envelope_id = 'b01b1b76-8b9e-47bb-806a-7cc32be98d4d'
    envelope_list = pd.read_csv(filename).to_dict(orient='records')

    dsc = DocuSignClient(client_id, impersonated_user, False, private_key)

    log_file = open("log.txt", "w")

    print(datetime.now())

    for index, envelope in enumerate(envelope_list):
        print(str(index) + ' de ' + str(len(envelope_list)))

        status_code, response = dsc.get_envelope_info(envelope['envelope'])

        if status_code == 200:
            status = response['status']
            log_file.write(str(envelope['envelope']) + '#' + str(status) + '\n')
        else:
            log_file.write(str(envelope['envelope']) + ' - ' + str(response['errorCode']) + ' - ' + response['message'] + '\n')

    log_file.close()
    print(datetime.now())


if __name__ == "__main__":
    get_envelope_info()
