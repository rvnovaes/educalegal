from datetime import datetime
from mongoengine import *

from .constants import VALID_FIELD_TYPES


def create_mongo_connection(db, alias, username, password, host, port):
    connect(db, alias, username=username, password=password, host=host, port=port)


def get_field(field_type, required):

    if field_type == "BooleanField":
        field = BooleanField()
    if field_type == "DateTimeField":
        field = DateTimeField()
    if field_type == "EmailField":
        field = EmailField()
    if field_type == "FloatField":
        field = FloatField()
    if field_type == "IntField":
        field = IntField()
    if field_type == "StringField":
        field = StringField()
    if required:
        field.required = True
    return field


def create_dynamic_document_class(
    class_name: str,
    field_properties_dict: dict,
    required_properties_dict: dict,
    parent_fields_dict: dict,
    **kwargs
):
    # Cria o dicionario de atributos que será usado na classe dinamica
    custom_attributes = dict()
    for key, value in field_properties_dict.items():
        required = required_properties_dict[key]
        parent = parent_fields_dict[key]
        if required.lower() == "true":
            required = True
        else:
            required = False
        # Os nomes de coluna no Mongo nao podem ter pontos.
        key = key.replace(".", "_")
        custom_attributes[key] = get_field(value, required)

        # insere o nome do objeto que contem o campo
        custom_attributes[key].__setattr__('parent', parent)

    try:
        custom_attributes["selected_school"].choices = kwargs["school_names_set"]
    except KeyError:
        pass
    try:
        custom_attributes["school_division"].choices = kwargs["school_units_names_set"]
    except KeyError:
        pass

    # Adiciona campo de data de criacao
    custom_attributes["created"] = DateTimeField(default=datetime.now())
    custom_attributes["created"].__setattr__('parent', None)

    # Cria a classe de documento dinamica
    DynamicDocumentClass = type(class_name, (Document,), custom_attributes)

    return DynamicDocumentClass


def _remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def mongo_to_hierarchical_dict(document, exclude_fields=('id',)):
    """Monta a estrutura do dicionário em níveis de acordo com os objetos do Docassemble"""

    document_dict = dict()
    for field in document._fields:
        # ignora o id pois ele nao tem o atributo parent
        if field in exclude_fields:
            document_dict[field] = document[field]
            continue

        if document._fields[field].parent:
            # remove o prefixo (objeto pai) dos campos
            prefix = document._fields[field].parent + '_'
            field_name = _remove_prefix(field, prefix)

            # verifica se a chave pai já existe no dict
            if not document._fields[field].parent in document_dict:
                document_dict[document._fields[field].parent] = dict()

            document_dict[document._fields[field].parent][field_name] = document[field]
        else:
            document_dict[field] = document[field]

    return document_dict
