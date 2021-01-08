import logging

from os.path import join
from pathlib import Path
from urllib.request import urlretrieve

from django.conf import settings


def save_file_from_url_in_disk(url, relative_path, filename):
    """
    Faz o download e salva o arquivo no caminho especificado, dentro do diretorio base em web/media
    :param url: url da qual será feito o download
    :param relative_path: diretório onde será salvo o arquivo. É concatenado com o diretório base.
        Ex.: path = docassemble, será salvo em /opt/educalegal/web/media/docassemble
    :param filename: nome do arquivo a ser salvo
    :return: Caminho absoluto e relativo do arquivo
    """
    # salva o arquivo em media/path
    fullpath = join(settings.BASE_DIR, "media/", relative_path)

    # cria diretorio e subdiretorio, caso nao exista
    Path(fullpath).mkdir(parents=True, exist_ok=True)

    absolute_path = join(fullpath, filename)

    relative_file_path = join(relative_path, filename)

    # baixa o arquivo no diretorio criado
    try:
        urlretrieve(url, absolute_path)
    except Exception as e:
        message = 'Não foi possível salvar o arquivo no sistema de arquivos. Erro: ' + str(e)
        logging.exception(message)
        return message, ''

    return absolute_path, relative_file_path


def delete_keys_from_obj(obj, keys_to_delete):
    """Apaga recursivamente os itens não desejados do dicionário ou da lista.
    :param
        obj - dicionário ou lista de onde serão excluídos os itens
        keys_to_delete - string ou lista de chaves que devem ser excluídas
    :return
        obj - dicionário ou lista com os itens excluídos
    """
    if isinstance(keys_to_delete, str):
        keys_to_delete = [keys_to_delete]

    if isinstance(obj, dict):
        for key in set(keys_to_delete):
            if key in obj:
                del obj[key]
        for k, v in obj.items():
            delete_keys_from_obj(v, keys_to_delete)
    elif isinstance(obj, list):
        for i in obj:
            delete_keys_from_obj(i, keys_to_delete)

    return obj
