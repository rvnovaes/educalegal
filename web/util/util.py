import logging
import os
import urllib.request

from pathlib import Path

from django.conf import settings


def save_file_from_url(url, relative_path, filename):
    """
    Faz o download e salva o arquivo no caminho especificado, dentro do diretorio base em web/media
    :param url: url da qual será feito o download
    :param relative_path: diretório onde será salvo o arquivo. É concatenado com o diretório base.
        Ex.: path = docassemble, será salvo em /opt/educalegal/web/media/docassemble
    :param filename: nome do arquivo a ser salvo
    :return: Caminho absoluto e relativo do arquivo
    """
    # salva o arquivo em media/path
    fullpath = os.path.join(settings.BASE_DIR, "media/", relative_path)

    # cria diretorio e subdiretorio, caso nao exista
    Path(fullpath).mkdir(parents=True, exist_ok=True)

    absolute_path = os.path.join(fullpath, filename)

    relative_file_path = os.path.join(relative_path, filename)

    # baixa o arquivo no diretorio criado
    try:
        urllib.request.urlretrieve(url, absolute_path)
    except Exception as e:
        message = 'Não foi possível salvar o arquivo no sistema de arquivos. Erro: ' + str(e)
        logging.exception(message)
        return message

    return absolute_path, relative_file_path
