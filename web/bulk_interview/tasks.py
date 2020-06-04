from __future__ import absolute_import, unicode_literals
import logging
import requests

from celery import shared_task
from .docassemble_client import DocassembleClient, DocassembleAPIException
from urllib3.exceptions import NewConnectionError

logger = logging.getLogger(__name__)

@shared_task
def create_document(base_url, api_key, username, user_password, interview_full_name, interview_variables):
    try:
        dac = DocassembleClient(base_url, api_key)
        logger.info(
            "Dados do servidor de entrevistas: {base_url} - {api_key}".format(
                base_url=base_url, api_key=api_key
            )
        )
    except NewConnectionError as e:
        message = "Não foi possível estabelecer conexão com o servidor de geração de documentos. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise NewConnectionError(message)
    else:
        try:
            response_json, status_code = dac.secret_read(username, user_password)
            secret = response_json
            logger.info(
                "Secret obtido do servidor de geração de documentos: {secret}".format(
                    secret=secret
                )
            )
        except requests.exceptions.ConnectionError as e:
            message = "Não foi possível obter o secret do servidor de geração de documentos. | {e}".format(
                e=str(e)
            )
            logger.error(message)
            raise DocassembleAPIException(message)
        else:
            if status_code != 200:
                error_message = "Erro ao gerar o secret | Status Code: {status_code} | Response: {response}".format(
                    status_code=status_code, response=response_json
                )
                logger.error(error_message)
                raise requests.exceptions.ConnectionError(error_message)
            else:
                try:
                    (
                        interview_session,
                        response_json,
                        status_code,
                    ) = dac.start_interview(interview_full_name, secret)
                    logger.info(
                        "Sessão da entrevista gerada com sucesso: {interview_session}".format(
                            interview_session=interview_session
                        )
                    )
                except requests.exceptions.ConnectionError as e:
                    message = "Não foi possível iniciar nova sessão de entrevista. | {e}".format(
                        e=str(e)
                    )
                    logger.error(message)
                    raise DocassembleAPIException(message)
                else:
                    if status_code != 200:
                        message = "Erro ao iniciar nova sessão | Status Code: {status_code} | Response: {response}".format(
                            status_code=status_code, response=response_json
                        )
                        logger.error(message)
                        raise DocassembleAPIException(message)
                    else:
                        try:
                            logger.info(
                                "Tentando gerar entrevista {interview_full_name} com os dados {interview_variables}".format(
                                    interview_full_name=interview_full_name,
                                    interview_variables=interview_variables,
                                )
                            )
                            response, status_code = dac.interview_set_variables(
                                secret,
                                interview_full_name,
                                interview_variables,
                                interview_session,
                            )
                        except Exception as e:
                            message = str(e)
                            logger.error(message)
                            raise DocassembleAPIException(message)
                        else:
                            if status_code != 200:
                                message = "Erro ao gerar entrevista | Status Code: {status_code} | Response: {response}".format(
                                    status_code=status_code,
                                    response=str(response.text),
                                )
                                logger.error(message)
                                DocassembleAPIException(message)
                            else:
                                if interview_variables["submit_to_esignature"]:
                                    status_code = dac.interview_run_action(
                                        secret,
                                        interview_full_name,
                                        interview_session,
                                        "submit_to_esignature",
                                        None,
                                    )
                                    logger.info(status_code)
                                message = "Status Code: {status_code} | Response: {response}".format(
                                    status_code=status_code,
                                    response=str(response),
                                )
                                logger.info(message)