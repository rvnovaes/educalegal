import csv
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
        field = EmailField()
    if field_type == "IntField":
        field = IntField()
    if field_type == "LongField":
        field = IntField()
    if field_type == "StringField":
        field = StringField()
    if required:
        field.required = True
    return field


def create_dynamic_document_class(class_name: str, field_properties_dict: dict, required_properties_dict: dict):
    # Cria o dicionario de atributos que será usado na classe dinamica
    custom_attributes = dict()
    for key, value in field_properties_dict.items():
        required = required_properties_dict[key]
        if required == "true":
            required = True
        else:
            required = False
        key = key.replace('.', '_')
        custom_attributes[key] = get_field(value, required)
    # Cria a classe de documento dinamica
    DynamicDocumentClass = type(class_name, (Document,), custom_attributes)

    return DynamicDocumentClass