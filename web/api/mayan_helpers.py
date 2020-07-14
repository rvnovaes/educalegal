from requests import Session
from retry_requests import retry

class MayanClient:
    def __init__(self, api_base_url, token):
        self.api_base_url = api_base_url
        headers = {"Authorization": "Token " + token}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=0.5,
            status_to_retry=(500, 502, 504, 404),
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
