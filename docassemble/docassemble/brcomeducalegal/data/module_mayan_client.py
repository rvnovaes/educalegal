from requests import Session

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

    def document_type_read(self, document_type_id):
        final_url = self.api_base_url + "/api/document_types/{id}".format(id=document_type_id)
        response = self.session.get(final_url).json()
        return response
