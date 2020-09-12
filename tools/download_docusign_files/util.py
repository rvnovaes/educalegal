import logging
import os
import urllib.request

from pathlib import Path


def save_file_from_url(url, filename):
    # salva o arquivo na pasta do projeto em .../docusign
    current_path = os.path.realpath(__file__)

    fullpath = os.path.join(current_path, 'docusign')

    # cria diretorio e subdiretorio, caso nao exista
    Path(fullpath).mkdir(parents=True, exist_ok=True)

    absolute_path = os.path.join(fullpath, filename)

    # baixa o arquivo no diretorio criado
    try:
        urllib.request.urlretrieve(url, absolute_path)
    except Exception as e:
        message = 'Não foi possível salvar o arquivo no sistema de arquivos. Erro: ' + str(e)
        logging.exception(message)
        return message

    return absolute_path
