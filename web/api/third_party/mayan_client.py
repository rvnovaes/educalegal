import io
import logging
import requests
import time

# https://github.com/bustawin/retry-requests
from retry_requests import retry


class MayanClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            requests.Session(),
            retries=3,
            backoff_factor=0.5,
            status_to_retry=(500, 502, 504),
        )
        self.session.headers.update(headers)

    def document_create(self, data, url, file):
        """Salva o arquivo no GED
        :param data: dados do arquivo
        :type: dict
        :param url: URL da qual o arquivo será baixado
        :type: str
        :param file: caminho no disco onde o arquivo foi salvo. É usado quando a URL não foi fornecida.
        :type: str
        :return: status_code
        :rtype: int
        :return: response.json()
        :rtype: dict
        :return: id do documento no GED
        :rtype: int
        """
        #
        # if file:
        #     f = file
        #     data = f.read()
        #     f.close()
        # else:
        #     data = None
        #
        # if data:
        #     encoded = base64.b64encode(data).decode()
        #     attachment = Attachment()

        if url:
            try:
                response = requests.get(url)
                file = io.BytesIO(response.content)
            except Exception as e:
                message = 'Erro ao salvar a url como arquivo temporário. Erro: {e}'.format(e=e)
                logging.error(message)
                return 400, message, 0
        # else:
        #     try:
        #         file = open(absolute_path, mode="rb")
        #     except Exception as e:
        #         message = 'Erro ao abrir o arquivo. Erro: {e}'.format(e=e)
        #         logging.error(message)
        #         return 400, message, 0

        # envia documento para o ged
        final_url = self.api_base_url + "/api/documents/"
        try:
            response = self.session.post(
                final_url, data=data, files={"file": file}
            )
        except Exception as e:
            message = 'Não foi possível salvar o documento no GED. Erro: ' + str(e)
            logging.error(message)
            return 400, message, 0
        else:
            if 'id' in response.json():
                return response.status_code, response.json(), response.json()['id']
            else:
                return response.status_code, response.json(), 0

    # Este método foi escrito deste modo para retornar uma mensagem num formato que o Docassemble pode interpretar
    # Não deve ser usado com chamados puros de API, apenas no contexto do Docassemble
    def document_read(self, document_id):
        final_url = self.api_base_url + "/api/documents/{id}".format(id=document_id)
        number_of_tries = 5
        try:
            for i in range(number_of_tries + 1):
                t = 0.5 * pow(2, (i - 1))
                response = self.session.get(final_url)
                if response.status_code == 404 and i < number_of_tries:
                    print(t)
                    time.sleep(t)
                elif response.status_code == 404 and i == number_of_tries:
                    error_message = (
                        "<h5>O documento não foi encontrado/criado no GED!</h5>"
                        "<b>Status Code :</b> {status_code}<br>"
                        "<b>Reason :</b> {reason}<br>"
                        "<b>URL do GED:</b> {url}<br><br>"
                    ).format(
                        status_code=str(response.status_code),
                        reason=response.reason,
                        url=response.url,
                    )
                    return error_message
                else:
                    return response.json()
        except requests.RequestException as e:
            error_message = (
                "<h5>O documento não foi criado no GED!</h5><br>"
                "<b>Exception:</b> {e}<br><br>"
            ).format(e=str(e))
            return error_message

    # Este método foi criado para não dar tratamento algum à resposta. Deve ser usado para chamadas de API.
    # O método document_read acima retorna uma mensagem que o Docassemble utiliza
    def document_simple_read(self, document_id):
        final_url = self.api_base_url + "/api/documents/{id}".format(id=document_id)
        response = self.session.get(final_url)
        return response

    def document_download(self, document_id):
        final_url = self.api_base_url + "/api/documents/{id}/download".format(id=document_id)
        response = self.session.get(final_url)
        return response

    def document_type_read(self, document_type_id):
        final_url = self.api_base_url + "/api/document_types/{id}".format(id=document_type_id)
        response = self.session.get(final_url).json()
        return response

    def document_bulk_delete(self, start_id, end_id, delete_from_trash=True):
        for document_id in range(start_id, end_id + 1):
            final_url = self.api_base_url + "/api/documents/{id}".format(id=document_id)
            response = self.session.delete(final_url)
            if response.status_code == 404:
                print('ID não encontrado: {id}'.format(id=document_id))
            elif response.status_code == 204:
                print('ID removido: {id}'.format(id=document_id))

                if delete_from_trash:
                    start_id = end_id = document_id
                    self.trashed_documents_bulk_delete(start_id, end_id)

        return response

    def trashed_documents_bulk_delete(self, start_id, end_id):
        for document_id in range(start_id, end_id + 1):
            final_url = self.api_base_url + "/api/trashed_documents/{id}".format(id=document_id)
            response = self.session.delete(final_url)
            if response.status_code == 404:
                print('ID não encontrado: {id}'.format(id=document_id))
            elif response.status_code == 204:
                print('ID removido da lixeira: {id}'.format(id=document_id))
        return response
