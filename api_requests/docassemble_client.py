import json

from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry


class DocassembleClient:
    def __init__(self, api_base_url, key):
        self.api_base_url = api_base_url
        headers = {"X-API-Key": key}
        self.session = retry(
            Session(),
            retries=3,
            backoff_factor=1,
            status_to_retry=(500, 502, 504),
        )
        self.session.headers.update(headers)

    def secret_read(self, username, password):
        """ Obtain a decryption key for a user """

        final_url = self.api_base_url + "/api/secret"
        payload = {'username': username, 'password': password}
        response = self.session.get(final_url, params=payload)
        return response.json()

    def user_interviews_list(self):
        """ List interviews of the user """

        final_url = self.api_base_url + "/api/user/interviews"
        response = self.session.get(final_url)
        return response.json()

    def session_read(self, interview_name):
        """ Start an interview session """

        final_url = self.api_base_url + "/api/session/new"
        payload = {'i': interview_name}
        response = self.session.get(final_url, params=payload).json()
        session = response['session']
        return session

    def interview_set_variables(self, interview_name, variables):
        """ Set variables in an interview
            variables - dict with all the variables for the interview
        """
        session = self.session_read(interview_name)

        final_url = self.api_base_url + "/api/session"
        data = {'i': interview_name, 'session': session, 'variables': json.dumps(variables)}
        response = self.session.post(final_url, data=data)
        return response.json()
