import logging
import os
from pathlib import Path
import urllib.request

from django.conf import settings


def save_file_from_url(url, path, filename):
    """
    Faz o download e salva o arquivo no caminho especificado, dentro do diretorio base em web/media
    :param url: url da qual será feita o download
    :param path: caminho onde será salvo o arquivo. É concatenado com o diretório base.
        Ex.: path = docassemble, será salvo em /opt/educalegal/web/media/docassemble
    :param filename: nome do arquivo a ser salvo
    :return: Caminho absoluto do arquivo e nome do arquivo
    """
    # salva o arquivo em media/path
    fullpath = os.path.join(settings.BASE_DIR, "media/", path)

    # cria diretorio e subdiretorio, caso nao exista
    Path(fullpath).mkdir(parents=True, exist_ok=True)

    absolute_path = os.path.join(fullpath, filename)

    logging.info("url_absolute_path")
    logging.info(url)
    logging.info(absolute_path)
    # baixa o pdf no diretorio criado
    try:
        urllib.request.urlretrieve(url, absolute_path)
    except Exception as e:
        message = 'Não foi possível salvar o arquivo no sistema de arquivos. Erro: ' + str(e)
        logging.exception(message)
        return message, ''

    return absolute_path, filename
