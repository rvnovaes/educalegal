import logging
import math
import numbers
import re
import pandas as pd
from validator_collection import validators, checkers, errors
import numpy as np


from .constants import VALID_FIELD_TYPES

logger = logging.getLogger(__name__)


def is_dataframe_empty(bulk_data: pd.DataFrame):
    if bulk_data.empty:
        raise ValueError("O arquivo CSV está vazio")
    else:
        return False


def is_field_empty(field_name, field_type_name):
    if not checkers.is_not_empty(field_type_name):
        raise ValueError("O tipo de campo para {field_name} não pode ser vazio.".format(field_name=field_name))
    # Testa se é número, pois nan é número
    elif isinstance(field_type_name, numbers.Number):
        raise ValueError("O tipo de campo para {field_name} não pode ser vazio.".format(field_name=field_name))
    else:
        return False


def is_field_type_metadata_valid(field_name, field_type_name):
    is_field_empty(field_name, field_type_name)
    if field_type_name not in VALID_FIELD_TYPES:
        raise ValueError("O tipo de campo para {field_name} não pode ser {field_type_name}. Deve ser um dos seguintes: BooleanField, DateTimeField, EmailField, FloatField, IntField, LongField ou StringField".format(field_name=field_name, field_type_name=field_type_name))
    else:
        return True


def is_boolean_flag_valid(field_name, field_boolean_name):
    is_field_empty(field_name, field_boolean_name)
    field_boolean_name = field_boolean_name.lower()
    if field_boolean_name not in ["true", "false"]:
        raise ValueError("O valor de verdadeiro ou false para {field_name} não pode ser {field_boolean_name}. Deve ser true ou false.".format(field_name=field_name, field_boolean_name=field_boolean_name))
    else:
        return True


def is_csv_metadata_valid(bulk_data: pd.DataFrame):
    if not isinstance(bulk_data, pd.DataFrame):
        raise ValueError("O valor não é um Dataframe Pandas")
    is_dataframe_empty(bulk_data)
    # A zeresima linha representa os tipos dos campos
    # Testa se os tipos de campos estão todos preenchidos e pertencem à lista BooleanField,
    # DateTimeField, EmailField, FloatField, IntField, LongField ou StringField
    field_types_dict = bulk_data.loc[0].to_dict()
    for k, v in field_types_dict.items():
        is_field_type_metadata_valid(k, v)

    # A primeira linha representa se o campo e required (true / false) como string
    required_fields_dict = bulk_data.loc[1].to_dict()
    for k, v in required_fields_dict.items():
        is_boolean_flag_valid(k, v)
    return field_types_dict, required_fields_dict,  True


def is_csv_content_valid(bulk_data: pd.DataFrame):
    # Cria novo df apenas com os dados, sem as linhas de tipo, required e labels para usuário final
    # Lembre-se que a linha de header do df se mantem
    if not isinstance(bulk_data, pd.DataFrame):
        raise ValueError("O valor não é um Dataframe Pandas")

    bulk_data_content = bulk_data.drop(bulk_data.index[range(0, 4)])

    is_dataframe_empty(bulk_data_content)

    if "school_name" not in bulk_data_content.columns:
        raise ValueError("Não existe a coluna school_name. Ela é obrigatória.")

    if "unidadeAluno" not in bulk_data_content.columns:
        raise ValueError("Não existe a coluna unidadeAluno. Ela é obrigatória.")

    # Substitui os campos de unidade escolar vazios, aos quais o Pandas havia atribuido nan, por ---
    bulk_data_content["unidadeAluno"] = bulk_data_content["unidadeAluno"].replace({np.nan: "---"})
    # Substitui os campos vazios, aos quais o Pandas havia atribuido nan, por None
    bulk_data_content = bulk_data_content.replace({np.nan: None})

    return bulk_data_content, True

