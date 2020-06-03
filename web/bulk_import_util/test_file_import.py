import pytest
import os
from datetime import datetime


script_dir = os.path.dirname(__file__)

from .file_import import *


@pytest.fixture
def valid_csv():
    with open(os.path.join(script_dir, "sample_data_sources/valid.csv")) as csvfile:
        valid_data = pd.read_csv(csvfile, sep="#")
    return valid_data


@pytest.fixture
def only_headers():
    with open(os.path.join(script_dir, "sample_data_sources/only_headers.csv")) as csvfile:
        empty = pd.read_csv(csvfile, sep="#")
    return empty


@pytest.fixture
def empty_content():
    with open(os.path.join(script_dir, "sample_data_sources/empty_content.csv")) as csvfile:
        empty_content_fixture = pd.read_csv(csvfile, sep="#")
    return empty_content_fixture


@pytest.fixture
def metadata_fixture():
    with open(os.path.join(script_dir, "sample_data_sources/metadata_fixture.csv")) as csvfile:
        metadata_fixture = pd.read_csv(csvfile, sep="#")
    return metadata_fixture


@pytest.fixture
def no_school_name():
    with open(os.path.join(script_dir, "sample_data_sources/no_school_name_columnn.csv")) as csvfile:
        no_school_name_fixture = pd.read_csv(csvfile, sep="#")
    return no_school_name_fixture

@pytest.fixture
def no_unidadeAluno():
    with open(os.path.join(script_dir, "sample_data_sources/no_unidadeAluno_column.csv")) as csvfile:
        no_unidadeAluno_fixture = pd.read_csv(csvfile, sep="#")
    return no_unidadeAluno_fixture


def test_only_headers(only_headers):
    with pytest.raises(ValueError):
        is_dataframe_empty(only_headers)


def test_empty_content(empty_content):
    with pytest.raises(ValueError):
        is_dataframe_empty(empty_content.drop(empty_content.index[range(0, 4)]))


def test_not_empty_data_frame(valid_csv):
    assert is_dataframe_empty(valid_csv) is False


def test_field_type_metadata(metadata_fixture):
    metadata_fixture = metadata_fixture.loc[0].to_dict()
    assert is_field_empty("valid_field", metadata_fixture["valid_field"]) is False
    assert is_field_type_metadata_valid("valid_field", metadata_fixture["valid_field"]) is True
    with pytest.raises(ValueError):
        is_field_empty("empty_type_name", metadata_fixture["empty_type_name"])
    with pytest.raises(ValueError):
        is_field_type_metadata_valid("empty_type_name", metadata_fixture["empty_type_name"])
    with pytest.raises(ValueError):
        is_field_type_metadata_valid("wrong_type_name", metadata_fixture["wrong_type_name"])


def test_boolean_flag_metadata(metadata_fixture):
    metadata_fixture = metadata_fixture.loc[1].to_dict()
    assert is_field_empty("valid_field", metadata_fixture["valid_field"]) is False
    assert is_boolean_flag_valid("valid_field", metadata_fixture["valid_field"]) is True
    with pytest.raises(ValueError):
        is_field_empty("empty_boolean_flag", metadata_fixture["empty_boolean_flag"])
    with pytest.raises(ValueError):
        is_boolean_flag_valid("empty_boolean_flag", metadata_fixture["empty_boolean_flag"])
    with pytest.raises(ValueError):
        is_boolean_flag_valid("wrong_boolean_flag", metadata_fixture["wrong_boolean_flag"])


def test_valid_csv_metadata(valid_csv):
    field_types_dict, required_fields_dict, is_csv_valid = is_csv_metadata_valid(valid_csv)
    assert is_csv_valid is True


def test_invalid_csv_metadata(only_headers):
    with pytest.raises(ValueError):
        is_csv_metadata_valid(only_headers)


def test_no_school_column(no_school_name):
    with pytest.raises(ValueError):
        is_csv_content_valid(no_school_name)


def test_no_unidadeAluno(no_unidadeAluno):
    with pytest.raises(ValueError):
        is_csv_content_valid(no_unidadeAluno)

def test_string_date_format():
    assert string_date_format("12/12/2020") == datetime.strptime("12/12/2020", "%d/%m/%Y")
    assert string_date_format("1/1/2020") == datetime.strptime("01/01/2020", "%d/%m/%Y")

    with pytest.raises(ValueError):
        string_date_format("1/1")
    with pytest.raises(ValueError):
        string_date_format("1|1|1")
    with pytest.raises(ValueError):
        string_date_format("01-01")
    with pytest.raises(ValueError):
        string_date_format("01/01/20")
    with pytest.raises(ValueError):
        string_date_format("31/01/20")
    with pytest.raises(ValueError):
        string_date_format("1-dez-2020")
    with pytest.raises(ValueError):
        string_date_format("1/dez/2020")
    with pytest.raises(ValueError):
        string_date_format("12/31/2020") # formato estadunidense
    with pytest.raises(ValueError):
        string_date_format("2020-05-01")













