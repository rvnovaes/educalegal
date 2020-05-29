from datetime import datetime
from mongoengine import *


def create_mongo_connection(db, alias, username, password, host, port):
    connect(db, alias, username=username, password=password, host=host, port=port)


def get_field(field_type, required):
    if field_type == "BooleanField":
        field = BooleanField()
    if field_type == "DateTimeField":
        field = DateTimeField()
    if field_type == "DecimalField":
        field = DecimalField()
    if field_type == "EmailField":
        field = EmailField()
    if field_type == "FloatField":
        field = FloatField()
    if field_type == "IntField":
        field = IntField()
    if field_type == "LongField":
        field = LongField()
    if field_type == "StringField":
        field = StringField()
    if required:
        field.required = True
    return field


def create_dynamic_document_class(
    class_name: str,
    field_properties_dict: dict,
    required_properties_dict: dict,
    **kwargs
):
    # Cria o dicionario de atributos que será usado na classe dinamica
    custom_attributes = dict()
    for key, value in field_properties_dict.items():
        required = required_properties_dict[key]
        if required.lower() == "true":
            required = True
        else:
            required = False
        # Os nomes de coluna no Mongo nao podem ter pontos.
        key = key.replace(".", "_")
        custom_attributes[key] = get_field(value, required)

    try:
        custom_attributes["selected_school"].choices = kwargs["school_names_set"]
    except KeyError:
        pass
    try:
        custom_attributes["unidadeAluno"].choices = kwargs["school_units_names_set"]
    except KeyError:
        pass

    # Adiciona campo de data de criacao
    custom_attributes["created"] = DateTimeField(default=datetime.now())

    # Cria a classe de documento dinamica
    DynamicDocumentClass = type(class_name, (Document,), custom_attributes)

    return DynamicDocumentClass


# helper.py
def mongo_to_dict(obj, exclude_fields):
    return_data = []

    if obj is None:
        return None

    if isinstance(obj, Document):
        return_data.append(("id", str(obj.id)))

    for field_name in obj._fields:

        if field_name in exclude_fields:
            continue

        if field_name in ("id",):
            continue

        data = obj._data[field_name]

        if isinstance(obj._fields[field_name], ListField):
            return_data.append((field_name, list_field_to_dict(data)))
        elif isinstance(obj._fields[field_name], EmbeddedDocumentField):
            return_data.append((field_name, mongo_to_dict(data, [])))
        elif isinstance(obj._fields[field_name], DictField):
            return_data.append((field_name, data))
        else:
            return_data.append(
                (field_name, mongo_to_python_type(obj._fields[field_name], data))
            )

    return dict(return_data)


def list_field_to_dict(list_field):
    return_data = []

    for item in list_field:
        if isinstance(item, EmbeddedDocument):
            return_data.append(mongo_to_dict(item, []))
        else:
            return_data.append(mongo_to_python_type(item, item))

    return return_data


def mongo_to_python_type(field, data):
    if isinstance(field, DateTimeField):
        return str(data.isoformat())
    elif isinstance(field, ComplexDateTimeField):
        return field.to_python(data).isoformat()
    elif isinstance(field, StringField):
        return str(data)
    elif isinstance(field, FloatField):
        return float(data)
    elif isinstance(field, IntField):
        return int(data)
    elif isinstance(field, BooleanField):
        return bool(data)
    elif isinstance(field, ObjectIdField):
        return str(data)
    # Decimal nao e serializavel, por isso transformacao em float
    elif isinstance(field, DecimalField):
        return float(data)
    else:
        return str(data)
