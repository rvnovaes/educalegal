from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task
import json

from urllib3.exceptions import NewConnectionError
from requests.exceptions import ConnectionError

from api.third_party.docassemble_client import DocassembleClient, DocassembleAPIException, DocumentNotGeneratedException

from .util import send_email, send_to_esignature


logger = logging.getLogger(__name__)
count_down = 5


def create_secret(base_url, api_key, username, user_password):
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
        raise DocassembleAPIException(message)
    else:
        try:
            response_json, status_code = dac.secret_read(username, user_password)
            secret = response_json
            logger.info(
                "Secret obtido do servidor de geração de documentos: {secret}".format(
                    secret=secret
                )
            )
        except ConnectionError as e:
            message = "Não foi possível obter o secret do servidor de geração de documentos. | {e}".format(
                e=str(e)
            )
            logger.error(message)
            raise DocassembleAPIException(message)
        else:
            if status_code != 200:
                error = "Erro ao gerar o secret | Status Code: {status_code} | Response: {response}".format(
                    status_code=status_code, response=response_json
                )
                logger.error(error)
                raise DocassembleAPIException(error)
            else:
                return secret


@shared_task(bind=True, max_retries=3)
def celery_create_document(self, base_url, api_key, secret, interview_full_name, interview_variables):
# def celery_create_document(base_url, api_key, secret, interview_full_name, interview_variables):
    try:
        dac = DocassembleClient(base_url, api_key)

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
            raise ConnectionError(message)
        else:
            logger.info(
                "Tentando gerar entrevista {interview_full_name} para o documento {doc_uuid} ...".format(
                    interview_full_name=interview_full_name,
                    doc_uuid=interview_variables["url_args"]["doc_uuid"]
                )
            )

            response, status_code = dac.interview_set_variables(
                secret, interview_full_name, interview_variables, interview_session,
            )

            if status_code != 200:
                message = "Erro ao gerar entrevista | Status Code: {status_code} | Response: {response}".format(
                    status_code=status_code, response=str(response),
                )
                logger.error(message)
                raise DocumentNotGeneratedException(message)
            else:
                logger.info('Resposta da chamada interview_set_variables:')
                logger.info(response)

                try:
                    if response["questionText"] == "Seu documento foi gerado com sucesso!":
                        message = "Mensagem de criação de arquivos: {created_file_name}".format(
                            created_file_name=response["subquestionText"]
                        )
                        logger.info(message)

                        doc_uuid = interview_variables["url_args"]["doc_uuid"]
                    else:
                        raise DocumentNotGeneratedException(json.dumps(response))
                except KeyError:
                    raise DocumentNotGeneratedException(json.dumps(response))

            return doc_uuid

    except NewConnectionError as e:
        message = "Não foi possível estabelecer conexão com o servidor de geração de documentos. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down ** self.request.retries)

    except ConnectionError as e:
        message = "Não foi possível iniciar nova sessão de entrevista. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down ** self.request.retries)

    except DocumentNotGeneratedException as e:
        message = "Não foi exibida a tela final com a mensagem 'Seu documento foi gerado com sucesso!' | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down ** self.request.retries)

    except TypeError as e:
        message = "Erro na geração em lote. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down ** self.request.retries)

    except KeyError as e:
        message = "Não foi possível identificar algumas chaves na resposta do servidor. | {e}".format(
            e=str(e)
        )
        logger.error(message)
        raise self.retry(e=e, countdown=count_down ** self.request.retries)

    except Exception as e:
        message = "Houve um erro na criação do documento | {exc}".format(
            exc=str(type(e).__name__) + " : " + str(e)
        )
        logger.error(message)
        raise


@shared_task(bind=True, max_retries=3)
def celery_submit_to_esignature(self, doc_uuid):
# def celery_submit_to_esignature(doc_uuid):
    try:
        status_code, response = send_to_esignature(doc_uuid)
        if status_code != 201 and status_code != 202:
            message = "Houve um erro no envio para a assinatura eletrônica | {}".format(response)
            logger.error(message)
            self.retry(exc=message)
            self.update_state(state='FAILURE')

        return status_code, response
    except Exception as e:
        message = "Houve um erro no envio para a assinatura eletrônica | {e}".format(
            e=str(type(e).__name__) + " : " + str(e)
        )
        logger.error(message)
        self.retry(exc=e)
        raise


@shared_task(bind=True, max_retries=3)
def celery_send_email(self, doc_uuid):
# def celery_send_email(doc_uuid):
    try:
        status_code, response = send_email(doc_uuid)
        if status_code != 202:
            message = "Houve um erro no envio do e-mail | {}".format(response)
            logger.error(message)
            self.retry(exc=message)
            self.update_state(state='FAILURE')

        return status_code, response
    except Exception as e:
        message = "Houve um erro no envio do e-mail | {e}".format(
            e=str(type(e).__name__) + " : " + str(e)
        )
        logger.error(message)
        self.retry(exc=e)
        raise
