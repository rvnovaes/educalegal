import logging
import os
import pandas as pd
import urllib.request

from pathlib import Path

from api.third_party.docusign_client import DocuSignClient


# ------- ATENÇÃO - DADOS DE PRODUCAO DA BAHEMA -------
client_id = "120eefb3-a639-4ac7-a859-67d997c9222a"
impersonated_user = '02de7724-770a-4a11-8c2c-c6a400d26ae5'
private_key = '''-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAhI+rPxItTLdEIxeufYQdlSFLEGI7AbdGmp7L99aafDrSRQ+e
/AUjcqwF+hwOrjHH1qK0T2v07/V6xRLizB0avN/PaUf7Pixv7RcY3/TS90OpK+mx
G/HzLZI3c16DmJmOE9pONvb8jnjtkkKEUqGHA0kGRb7oJm7Ce4Cw5GeXKdcMcWHb
2xAt491gIIlCO4frjQ7KN4yXG41N0Zx5BdI8C2fdaNekyMPe1Wt12WFgl6vJOd2T
ZXy3+uTE6RR7X+e4umb25/+eLVMOqiRrwpJPH9ZZHUUuxsoMVSnh5hvP6bEzQmHe
TEBt/Ikbv7J93T1ONCQ2wj03ntpiZNYQLf667wIDAQABAoIBAB5VU83MZoJCA3z2
O87r7usDoc4fdDopyqWyBaFyQYqA2UHFV896i4h/daSsS+2vZXenZpQv823/Ybb7
4drsJASpQChquMKa34fEu8PvnWDIYksyn/zxigBZD4g+TeWa6aiAUVqBfPxLDq3j
u6y+2oq1aJKII048FRO2uIOjcrM3dapp+KMsnvmQVMJgTtT+kwH76khkvgxcIXEJ
cof2oEm9BbNsH9u3pv2aObm94OXuGk74bkvjX4Drkzec7qKlLPYmo2rW0iBa+CJR
QTrvOBMT7JrmPM+11ySkx6xmQN4sxTok6mZrSqhLg5qrHtlVZJ6G0Cahbd1SKXH0
Gh2CSWECgYEA1Lfi0eAmcquqL+kKsMnIhffxbr8MnQnd0SWu5xKiF+01BFIt4bH3
jGMihW38HNGjq07f94MBzkaae6eiQpXrhmnDrKxg6A8fhkW/4k7x+6iEjnFVOXQH
lYA1uAe6G5wuJ6bnR1v53excSqv8KZM6HsTqkw2s42hkpFmreGtB4qECgYEAn4iL
N8/1dwCG/+3MnJG4+mukkcI15lVrNTGk8R7PNas9VJZLeeAwXp0LD5uvyMY1/6rg
tCmIqBjERUrDotSfliFKa0PV3gSCIoBHjwWh5XmOR0X372rwBzuVdW3I7ztdCgnN
1XifyiuSDlCZcgbnUXmHSERxQH3qzu7cyJtBQ48CgYAl7hwt3FA+xkl0fZOAbpqo
+Ms+OibfobDB6HxFi9cHeS6o9JZl1jwT9mFjdXctFFyg4VGiauPZilFll0ChquXy
c82Gbr5g4sF2Sd2rVvRjMWthkufldMEdcV0i0Y3n+nNocqRu3wGxBsJ2NjCioTQN
5IMHcbrQWf8IJ00iDc4TwQKBgECvb6uAscm/t/1boWQ2nedD8CV9trcfGWonJ/bw
hBoBxctfaVkQcuxaBtscSElDPS/eTGAgmx11dVeXOf3y8oZAF1mo1rW/5DgzBVDT
etJ92BfEIgS8unhkS3SiwB9oVZA1a3VMBJZH1l/hhGY8sFxTx2ug/L6mj6e6KGFa
ujq3AoGASzqMNbXVH1k96HDYbvvEVWoDYDAIsSNHAjfEM8cUF0MrXfKT01f6pDNc
5uUMYZ+eJtgWNbmuFXpqIKXJOhFmoHJ2aerR2yddi3Ynxqml8uzgznYmZ+VpyFyZ
NUib6dhVqcVsbB3DSXX9nqsqjlAlUiKOUF9WedRSTTnuTw+mYyI=
-----END RSA PRIVATE KEY-----'''


def download_docusign_files():
    filename = 'bahema_docusign.csv'
    envelope_id = 'b01b1b76-8b9e-47bb-806a-7cc32be98d4d'
    # envelope_list = pd.read_csv(filename).to_dict(orient='records')

    dsc = DocuSignClient(client_id, impersonated_user, False, private_key)

    log_file = open("log.txt", "w")

    status_code, response = dsc.list_envelope_documents(envelope_id)

    if status_code == 200:
        documents = response['envelopeDocuments']
        for document in documents:
            status_code, url = dsc.get_envelope_document(envelope_id, document['documentId'])

            if status_code == 200:
                absolute_path = save_file_from_url(url, document['name'])
            else:
                # imprime log com arquivos nao baixados
                log_file.write(envelope_id)
    else:
        # imprime log com arquivos nao baixados
        log_file.write(envelope_id)

    log_file.close()

# for envelope in envelope_list:
#     status_code, response = dsc.list_envelope_attachments(envelope['envelope_id'])
#
#     if status_code == 200:
#         attachments = response['attachments']
#         for attachment in attachments:
#             status_code, response = dsc.get_envelope_attachment(envelope['envelope_id'], attachment['attachmentId'])


def save_file_from_url(url, filename):
    # salva o arquivo na pasta do projeto em .../docusign
    current_path = os.path.dirname(__file__)

    fullpath = os.path.join(current_path, 'docusign')

    # cria diretorio e subdiretorio, caso nao exista
    Path(fullpath).mkdir(parents=True, exist_ok=True)

    absolute_path = os.path.join(fullpath, filename)

    # baixa o arquivo no diretorio criado
    try:
        urllib.request.urlretrieve(url, absolute_path)
    except Exception as e:
        message = 'Não foi possível salvar o arquivo no sistema de arquivos. Erro: ' + str(e)
        logging.exception(message)
        return message

    return absolute_path


if __name__ == "__main__":
    download_docusign_files()
