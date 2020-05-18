import csv
from mongoengine import *


def create_mongo_connection(db, alias, username, password, host, port):
    connect(db, alias, username=username, password=password, host=host, port=port)


def get_field(field_name):
    if field_name == "BooleanField":
        return BooleanField()
    if field_name == "DateTimeField":
        return DateTimeField()
    if field_name == "DecimalField":
        return DecimalField()
    if field_name == "EmailField":
        return EmailField()
    if field_name == "FloatField":
        return EmailField()
    if field_name == "IntField":
        return IntField()
    if field_name == "LongField":
        return IntField()
    if field_name == "StringField":
        return StringField()


def create_dynamic_document_class(class_name: str, fields_dict: dict):
    # Cria o dicionario de atributos que será usado na classe dinamica
    custom_attributes = dict()
    for key, value in fields_dict.items():
        key = key.replace('.', '_')
        custom_attributes[key] = get_field(value)
    # Cria a classe de documento dinamica
    DinamicDocumentClass = type(class_name, (Document,), custom_attributes)

    return DinamicDocumentClass





if __name__ == "__main__":
    create_mongo_connection(
        "educalegal", "default", "educalegal", "educalegal", "localhost", 27017
    )
    class_name = "contrato_de_prestacao_de_servicos_educacionais"
    atrributes = dict()
    with open("contrato-prestacao-servicos-educacionais_v1.csv") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        rows = [r for r in reader]
    # Cria o dicionario de atributos que será usado na classe dinamica
    DynamicDocumentClass = create_dynamic_document_class(rows[0])

    # Grava cada uma das linhas
    normalized_headers_row = dict()
    for row in rows[1:]:
        for key, value in row.items():
            key = key.replace('.', '_')
            normalized_headers_row[key] = value
        dynamic_document = DynamicDocumentClass(**normalized_headers_row)
        dynamic_document.save()
