from __future__ import absolute_import, unicode_literals
import logging
from requests.exceptions import ConnectionError
import json
from urllib3.exceptions import NewConnectionError
from celery import shared_task

from .docassemble_client import DocassembleClient

logger = logging.getLogger(__name__)
count_down = 5


@shared_task(bind=True, max_retries=3)
def create_document(self, base_url, api_key, secret, interview_full_name, interview_variables
):
    try:
        dac = DocassembleClient(base_url, api_key)
        logger.info(
            "Dados do servidor de entrevistas: {base_url} - {api_key}".format(
                base_url=base_url, api_key=api_key
            )
        )
        interview_session, response_json, status_code = dac.start_interview(
                interview_full_name, secret
            )
        logger.info(
            "Sessão da entrevista gerada com sucesso: {interview_session}".format(
                interview_session=interview_session
            )
        )

        if status_code != 200:
            message = "Erro ao iniciar nova sessão | Status Code: {status_code} | Response: {response}".format(
                status_code=status_code, response=response_json
            )
            logger.error(message)
            raise self.retry(countdown=count_down**self.request.retries)
        else:
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

            if status_code != 200:
                message = "Erro ao gerar entrevista | Status Code: {status_code} | Response: {response}".format(
                    status_code=status_code, response=str(response.text),
                )
                logger.error(message)
                raise self.retry(countdown=count_down**self.request.retries)

            response_dict = json.loads(response.text)
            created_files = response_dict["attachments"][0][
                "filename_with_extension"
            ]
            message = "Criado(s) o(s) arquivo(s): {created_files}".format(
                created_files=created_files
            )
            logger.info(message)

            if interview_variables["submit_to_esignature"]:
                status_code = dac.interview_run_action(
                    secret,
                    interview_full_name,
                    interview_session,
                    "submit_to_esignature",
                    None,
                )

                logger.info(status_code)
                message = "Status Code da assinatura: {status_code}".format(status_code=status_code)
                logger.info(message)

    except NewConnectionError as e:
        message = "Não foi possível estabelecer conexão com o servidor de geração de documentos. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down**self.request.retries)

    except ConnectionError as e:
        message = "Não foi possível iniciar nova sessão de entrevista. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down**self.request.retries)

    except KeyError as e:
        message = "Não foi possível identificar os attachments na resposta do servidor de geração de documentos | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down**self.request.retries)

    except Exception as e:
        message = "Houve um erro inespecífico na criação do documento | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down** self.request.retries)