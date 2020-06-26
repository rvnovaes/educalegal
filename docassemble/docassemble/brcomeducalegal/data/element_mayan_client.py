import json
from requests import Session
import time
from requests.exceptions import RequestException

# https://github.com/bustawin/retry-requests
from retry_requests import retry


class MayanClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=0.5,
            status_to_retry=(500, 502, 504),
        )
        self.session.headers.update(headers)

    def document_create(
        self, filename, document_type, label="", language="", description=""
    ):
        file_object = open(filename, mode="rb")
        payload = {
            "document_type": document_type,
            "label": label,
            "language": language,
            "description": description,
        }
        final_url = self.api_base_url + "/api/documents/"
        response = self.session.post(
            final_url, data=payload, files={"file": file_object}
        )
        return response

    def document_create_message_docid(
        self, filename, document_type, label="", language="", description=""
    ):
        try:
            response = self.document_create(
                filename, document_type, label, language, description
            )
            if response.status_code == 201:
                returned_data = json.loads(response.text)
                success_message = (
                    "<b>Id:</b> {document_id}<br>"
                    "<b>Nome:</b> {document_label}<br>"
                    "<b>Status Code:</b> {status_code}<br>"
                    "<b>Reason:</b> {reason}<br>"
                ).format(
                    document_id=returned_data["id"],
                    document_label=returned_data["label"],
                    status_code=str(response.status_code),
                    reason=response.reason,
                    url=response.url,
                )
                return response.status_code, success_message, returned_data["id"]
            else:
                error_message = (
                    "<h5>O documento não foi criado no GED!</h5>"
                    "<b>Status Code :</b> {status_code}<br>"
                    "<b>Reason :</b> {reason}<br>"
                    "<b>URL do GED:</b> {url}<br><br>"
                ).format(
                    status_code=str(response.status_code),
                    reason=response.reason,
                    url=response.url,
                )
                return response.status_code, error_message, 0
        except RequestException as e:
            error_message = (
                "<h5>O documento não foi criado no GED!</h5><br>" 
                "<b>Exception:</b> {e}<br><br>"
            ).format(e=str(e))
        return error_message

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
                        "<h5>O documento não foi criado no GED!</h5>"
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
        except RequestException as e:
            error_message = (
                "<h5>O documento não foi criado no GED!</h5><br>"
                "<b>Exception:</b> {e}<br><br>"
            ).format(e=str(e))
            return error_message

    def document_type_read(self, document_type_id):
        final_url = self.api_base_url + "/api/document_types/{id}".format(id=document_type_id)
        response = self.session.get(final_url).json()
        return response
