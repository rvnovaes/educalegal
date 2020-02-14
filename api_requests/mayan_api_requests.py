import json
import requests
from requests.exceptions import RequestException


def document_create(url, headers, filename, document_type, label='', language='', description=''):
    file_object = open(filename, mode='rb')
    payload = {'document_type': document_type,
               'label': label,
               'language': language,
               'description': description
    }
    try:
        response = requests.post(url, headers=headers, data=payload, files={"file": file_object})
        if response.status_code == 201:
            returned_data = json.loads(response.text)
            success_message = '''
       Documento criado com sucesso!
       Id: {document_id}
       Nome: {document_label}
       {url}        
            '''.format(document_id=returned_data['id'], document_label=returned_data['label'], status_code=str(response.status_code), reason=response.reason, url=response.url)
            return success_message
        else:
            error_message = '''
       Falha ao enviar o documento para GED!
       Status Code : {status_code}
       Reason : {reason}
       URL do GED: {url}        
            '''.format(status_code=str(response.status_code), reason=response.reason, url=response.url)
    except RequestException as e:
        error_message = '''
       Falha ao enviar o documento para GED!            
       Exception: {e}        
        '''.format(e=str(e))
    return error_message


if __name__ == '__main__':
    url = 'http://localhost:8080/api/documents/'
    headers = {'Authorization': "Token c05a8402be65112e0164a0bce95c62db62bf7e25"}
    file = 'jupiter.jpg'
    document_type = 1
    label = 'jupiter'
    description = 'Juptiter Picture'

    document_create(url, headers, file, document_type, label=label, description=description)




