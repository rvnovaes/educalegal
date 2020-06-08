import json
import logging
from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry

logger = logging.getLogger(__name__)


class DocassembleAPIException(Exception):
    pass


class DocassembleClient:
    def __init__(self, base_url, admin_key):
        self.api_base_url = base_url
        headers = {"X-API-Key": admin_key}
        self.session = retry(
            Session(), retries=3, backoff_factor=1, status_to_retry=(500, 502, 504),
        )
        self.session.headers.update(headers)

    def secret_read(self, username, password):
        """ Obtain a decryption key for a user """

        final_url = self.api_base_url + "/api/secret"
        payload = {"username": username, "password": password}
        response = self.session.get(final_url, params=payload)

        return response.json(), response.status_code

    def config_read(self):
        """ Get the server configuration """

        final_url = self.api_base_url + "/api/config"
        response = self.session.get(final_url)
        return response.json()

    def user_interviews_list(self):
        """ Provides a filterable list of interview sessions stored on the system where the owner of the API is
        associated with the session """

        final_url = self.api_base_url + "/api/user/interviews"
        response = self.session.get(final_url)
        return response.json()

    def start_interview(self, interview_name, secret):
        """ Start an interview session """

        final_url = self.api_base_url + "/api/session/new"
        payload = {"i": interview_name, "secret": secret}

        response = self.session.get(final_url, params=payload)
        response_json = response.json()
        try:
            session = response_json["session"]
        except:
            session = None

        return session, response_json, response.status_code

    def interview_get_variables(self, secret, interview_name, session):
        final_url = self.api_base_url + "/api/session"

        payload = {
            "i": interview_name,
            "session": session,
            "secret": secret,
        }

        response = self.session.get(final_url, params=payload)
        return response.json(), response.status_code

    def interview_set_variables(self, secret, interview_name, variables, session):
        """ Set variables in an interview
            variables - dict with all the variables for the interview
        """

        final_url = self.api_base_url + "/api/session"
        logger.info("Final URL em interview_set_variables: " + final_url)

        variables = json.dumps(variables)

        payload = {
            "i": interview_name,
            "session": session,
            "secret": secret,
            "variables": variables,
        }
        logger.debug("Payload em interview_set_variables: " + str(payload))

        # response = self.session.post(final_url, json=payload)
        response = self.session.post(final_url, data=payload)
        return response.json(), response.status_code

    def interview_run_action(
        self, secret, interview_name, session, action, action_arguments=None
    ):
        final_url = self.api_base_url + "/api/session/action"

        payload = {
            "i": interview_name,
            "session": session,
            "secret": secret,
            "action": action,
            action_arguments: action_arguments,
        }

        response = self.session.post(final_url, data=payload)
        return response, response.status_code
