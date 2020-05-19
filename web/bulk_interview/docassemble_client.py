import json
import sys

from django.http import JsonResponse
from requests import Session

# https://github.com/bustawin/retry-requests
from retry_requests import retry


class DocassembleClient:
    def __init__(self, base_url, admin_key):
        self.api_base_url = base_url
        headers = {"X-API-Key": admin_key}
        self.session = retry(
            Session(), retries=3, backoff_factor=1, status_to_retry=(500, 502, 504),
        )
        self.session.headers.update(headers)

    def secret_read(self, key, username, password):
        """ Obtain a decryption key for a user """

        final_url = self.api_base_url + "/api/secret"
        payload = {"key": key, "username": username, "password": password}
        response = self.session.get(final_url, params=payload)

        return response.json()

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

        try:
            response = self.session.get(final_url, params=payload).json()
            session = response["session"]
            return session
        except Exception:
            extype, ex, tb = sys.exc_info()
            message = "Erro ao criar nova sessão. Response: {response}. Exception: {ex}".format(
                response=response, ex=ex.__str__()
            )
            raise Exception(message).with_traceback(ex.__traceback__)

    def interview_set_variables(self, secret, interview_name, variables, session):
        """ Set variables in an interview
            variables - dict with all the variables for the interview
        """

        final_url = self.api_base_url + "/api/session"

        payload = {
            "i": interview_name,
            "session": session,
            "secret": secret,
            "variables": json.dumps(variables),
        }

        try:
            response = self.session.post(final_url, data=payload)
            return response.json(), response.status_code
        except Exception as e:
            print("Erro: ", e.__class__.__name__)

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

        try:
            response = self.session.post(final_url, data=payload)
            return response.status_code
        except Exception as e:
            print("Erro: ", e.__class__.__name__)
