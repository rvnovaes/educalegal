import logging
from datetime import datetime
import numbers
import re
import pandas as pd
from validator_collection import validators, checkers, errors
from validator_collection_br import validators_br, checkers_br
import numpy as np

from util.constants import VALID_FIELD_TYPES

logger = logging.getLogger(__name__)


def is_dataframe_empty(bulk_data: pd.DataFrame):
    if bulk_data.empty:
        raise ValueError("O arquivo CSV está vazio ou contém apenas linhas de cabeçalho, sem nenhum dado.\n")
    else:
        return False


def is_field_empty(field_name, field_type_name):
    if not checkers.is_not_empty(field_type_name):
        raise ValueError(
            "O tipo de campo para {field_name} não pode ser vazio.\n".format(
                field_name=field_name
            )
        )
    # Testa se é número, pois nan é número
    elif isinstance(field_type_name, numbers.Number):
        raise ValueError(
            "O tipo de campo para {field_name} não pode ser vazio.\n".format(
                field_name=field_name
            )
        )
    else:
        return False


def is_field_type_metadata_valid(field_name, field_type_name):
    is_field_empty(field_name, field_type_name)
    if field_type_name not in VALID_FIELD_TYPES:
        raise ValueError(
            "O tipo de campo para {field_name} não pode ser {field_type_name}. Deve ser um dos seguintes: BooleanField, DateTimeField, EmailField, FloatField, IntField ou StringField.\n".format(
                field_name=field_name, field_type_name=field_type_name
            )
        )
    else:
        return True


def is_boolean_flag_valid(field_name, field_boolean_name):
    is_field_empty(field_name, field_boolean_name)
    field_boolean_name = field_boolean_name.lower()
    if field_boolean_name not in ["true", "false"]:
        raise ValueError(
            "O valor de verdadeiro ou false para {field_name} não pode ser {field_boolean_name}. Deve ser true ou false.\n".format(
                field_name=field_name, field_boolean_name=field_boolean_name
            )
        )
    else:
        return True


def is_csv_metadata_valid(bulk_data: pd.DataFrame):
    if not isinstance(bulk_data, pd.DataFrame):
        raise ValueError("O valor não é um Dataframe Pandas.\n")
    is_dataframe_empty(bulk_data)
    # A zeresima linha representa os tipos dos campos
    # Testa se os tipos de campos estão todos preenchidos e pertencem à lista
    # BooleanField, DateTimeField, EmailField, FloatField, IntField ou StringField
    field_types_dict = bulk_data.loc[0].to_dict()
    for k, v in field_types_dict.items():
        is_field_type_metadata_valid(k, v)

    # A primeira linha representa se o campo e required (true / false) como string
    required_fields_dict = bulk_data.loc[1].to_dict()
    for k, v in required_fields_dict.items():
        is_boolean_flag_valid(k, v)
    return field_types_dict, required_fields_dict, True


def is_csv_content_valid(bulk_data: pd.DataFrame):

    if not isinstance(bulk_data, pd.DataFrame):
        raise ValueError("O valor não é um Dataframe Pandas.\n")

    # Corta o df apenas nos os dados, sem as linhas: de tipo, required e labels para usuário final
    # para testar se os dados estão vazios
    # Lembre-se que a linha de header do df se mantem
    is_dataframe_empty(bulk_data.drop(bulk_data.index[range(0, 4)]))

    if "selected_school" not in bulk_data.columns:
        raise ValueError("Não existe a coluna selected_school. Ela é obrigatória.\n")

    if "school_division" not in bulk_data.columns:
        raise ValueError("Não existe a coluna school_division. Ela é obrigatória.\n")

    if "submit_to_esignature" not in bulk_data.columns:
        raise ValueError("Não existe a coluna submit_to_esignature. Ela é obrigatória.\n")

    if "el_send_email" not in bulk_data.columns:
        raise ValueError("Não existe a coluna el_send_email. Ela é obrigatória.\n")

    # Substitui os campos de unidade escolar vazios, aos quais o Pandas havia atribuido nan, por ---
    bulk_data["school_division"][4:] = bulk_data["school_division"][4:].replace({np.nan: "---"})

    # Substitui os campos vazios, aos quais o Pandas havia atribuido nan, por None
    bulk_data = bulk_data.replace({np.nan: None})

    # Cria dicionario para guardar o objeto (parent) de cada campo
    # A segunda linha do csv representa o objeto ao qual o campo pertence
    # Por exemplo: {"name_text": "notified"} significa que a propriedade name_text é de um notified (objeto Person/Individual)
    parent_fields_dict = bulk_data.loc[2].to_dict()

    error_messages = list()

    for column_name, column in bulk_data.iteritems():
        field_type_name = column[0]
        if column[1].lower() == 'true':
            field_required = True
        else:
            field_required = False
        for row_index, row_value in column[4:].items():
            try:
                validated_field_value, is_field_valid = validate_field(
                    column_name, row_index, field_type_name, field_required, row_value
                )
            except ValueError as e:
                message = (
                        str(type(e).__name__)
                        + " : "
                        + "Não foi possível validar ou converter o valor {row_value} da coluna {column_name} - linha: {row_index} em um campo tipo {field_type_name} - {field_required}.\n".format(
                    row_value=row_value, column_name=column_name, row_index=str(row_index + 2), field_type_name=field_type_name, field_required=field_required
                )
                        + str(e)
                )
                logger.error(message)
                error_messages.append(message)
            else:
                bulk_data[column_name].loc[row_index] = validated_field_value

        bulk_data_content = bulk_data.drop(bulk_data.index[range(0, 4)])

    if len(error_messages) > 0:
        csv_content_valid = False
    else:
        csv_content_valid = True

    return bulk_data_content, parent_fields_dict, error_messages, csv_content_valid


def validate_field(column_name, row_index, field_type_name, field_required, value):
    # Como foram removidas as linhas de cabeçalho, a orientação em relação ao número correto da linha soma-se 4
    row_index = row_index + 2
    if field_required is False and value is None:
        return value, True
    if field_required is True and value is None:
        raise errors.EmptyValueError(
            "Erro na coluna {column_name} de tipo {field_type_name}, linha {row_index}: o campo não "
            "pode ser vazio\n".format(
                column_name=column_name,
                row_index=row_index,
                value=value,
                field_type_name=field_type_name,
            )
        )
    else:
        is_valid = checkers.is_string(value, coerce_value=False)

        if not is_valid and checkers.is_string(value, coerce_value=True):
            value = validators.string(value, coerce_value=True)
        elif not is_valid:
            raise ValueError(
                "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                    column_name=column_name,
                    row_index=row_index,
                    value=value,
                    field_type_name=field_type_name,
                )
            )

        if field_type_name == "BooleanField":
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

            return value, True

        if field_type_name == "DateTimeField":

            value = string_date_format(value)

            is_valid = checkers.is_datetime(value, coerce_value=False)

            if is_valid and checkers.is_datetime(value, coerce_value=True):
                value = validators.datetime(value, coerce_value=True)
            elif not is_valid:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

            return value, True

        if field_type_name == "EmailField":

            is_valid = checkers.is_email(value, coerce_value=False)

            if is_valid and checkers.is_email(value, coerce_value=True):
                value = validators.email(value, coerce_value=True)
            elif not is_valid:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

            return value, True

        if field_type_name == "FloatField":
            value = float(value.replace(".", "").replace(",", "."))
            is_valid = checkers.is_float(value, coerce_value=False)

            if is_valid and checkers.is_float(value, coerce_value=True):
                value = validators.float(value, coerce_value=True)
            elif not is_valid:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

            return value, True

        if field_type_name == "IntField":
            is_valid = checkers.is_integer(value, coerce_value=False)

            if is_valid and checkers.is_integer(value, coerce_value=True):
                value = validators.integer(value, coerce_value=True)
            elif not is_valid:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

            return value, True

        if field_type_name == "CpfField":
            is_valid = checkers_br.is_cpf(value)

            if is_valid and checkers_br.is_cpf(value):
                value = validators_br.cpf(value)
            elif not is_valid:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

            return value, True

        if field_type_name == "CnpjField":
            is_valid = checkers_br.is_cnpj(value)

            if is_valid and checkers_br.is_cnpj(value):
                value = validators_br.cnpj(value)
            elif not is_valid:
                raise ValueError(
                    "Erro na coluna {column_name}, linha {row_index}: o valor {value} para o campo {field_type_name} não é válido.\n".format(
                        column_name=column_name,
                        row_index=row_index,
                        value=value,
                        field_type_name=field_type_name,
                    )
                )

        return value, True


def string_date_format(value: str) -> datetime:
    """

    :param value:
    :return:
    """
    # Encontre qq seq de digitos
    date_components = re.findall(r"[\d]+", value)
    if len(date_components) != 3:
        raise ValueError(
            "O formato de data deve ser dd/mm/aaaa. Não foi possível dividir o valor {value} em seus componentes numéricos.\n".format(
                value=value
            )
        )
    else:
        # Verifica os valores válidos para o dia
        day = date_components[0]
        try:
            day = validators.integer(day, coerce_value=True)
        except ValueError as e:
            message = (
                str(type(e).__name__)
                + " : "
                + "Não foi possível converter o valor {day} de {value} em um inteiro.\n".format(
                    day=str(day), value=value
                )
                + str(e)
            )
            logger.error(message)
            raise ValueError(message)
        else:
            if day > 31 or day == 0:
                raise ValueError(
                    "O dia do mês {day} é > 31 ou igual a zero em {value}. O formato de data deve ser dd/mm/aaaa.\n".format(
                        day=str(day), value=value
                    )
                )

        day = str(day).zfill(2)

        # Verifica os valores válidos para o mês
        month = date_components[1]
        try:
            month = validators.integer(month, coerce_value=True)
        except ValueError as e:
            message = (
                str(type(e).__name__)
                + " : "
                + "Não foi possível converter o valor {month} de {value} em um inteiro.\n".format(
                    month=month, value=value
                )
                + str(e)
            )
            logger.error(message)
            raise ValueError(message)
        else:
            if month > 12 or month == 0:
                raise ValueError(
                    "O mês {month} é > 12 ou igual a zero em {value}. O formato de data deve ser dd/mm/aaaa.\n".format(
                        month=str(month), value=value
                    )
                )

        month = str(month).zfill(2)

        # Verifica os valores válidos para o ano
        year = date_components[2]
        try:
            year = validators.integer(year, coerce_value=True)
        except ValueError as e:
            message = (
                str(type(e).__name__)
                + " : "
                + "Não foi possível converter o valor {year} de {value} em um inteiro.\n".format(
                    year=str(year), value=value
                )
                + str(e)
            )
            logger.error(message)
            raise ValueError(message)
        else:
            # Compara o valor do ano com zero e o comprimento da string do ano que deve ter 4 digitos
            if year == 0 or len(date_components[2]) < 4:
                raise ValueError(
                    "O ano deve possuir 4 dígitos e não pode ser igual a zero. O valor {year} em {value} não é válido.\n".format(
                        year=str(year), value=value
                    )
                )

        year = str(year).zfill(4)

        try:
            value = datetime.strptime(day + "/" + month + "/" + year, "%d/%m/%Y")
        except ValueError as e:
            message = (
                str(type(e).__name__)
                + " : "
                + "Não foi possível converter {value} em uma data.\n".format(value=value)
                + str(e)
            )
            logger.error(message)
            raise ValueError(message)

    return value
