import pytest
import os
from datetime import datetime


script_dir = os.path.dirname(__file__)

from .file_import import *


@pytest.fixture
def valid_csv_to_dataframe():
    with open(os.path.join(script_dir, "sample_data_sources/valid.csv")) as csvfile:
        valid_data = pd.read_csv(csvfile, sep="#")
    return valid_data


@pytest.fixture
def empty_csv_to_dataframe():
    with open(os.path.join(script_dir, "sample_data_sources/empty.csv")) as csvfile:
        empty = pd.read_csv(csvfile, sep="#")
    return empty


@pytest.fixture
def metadata_fixture():
    with open(os.path.join(script_dir, "sample_data_sources/metadata_fixture.csv")) as csvfile:
        metadata_fixture = pd.read_csv(csvfile, sep="#")
    return metadata_fixture


@pytest.fixture
def no_school_name_fixture():
    with open(os.path.join(script_dir, "sample_data_sources/no_school_name_columnn.csv")) as csvfile:
        no_school_name_fixture = pd.read_csv(csvfile, sep="#")
    return no_school_name_fixture

@pytest.fixture
def no_unidadeAluno_fixture():
    with open(os.path.join(script_dir, "sample_data_sources/no_unidadeAluno_column.csv")) as csvfile:
        no_unidadeAluno_fixture = pd.read_csv(csvfile, sep="#")
    return no_unidadeAluno_fixture



def test_empty_data_frame(empty_csv_to_dataframe):
    with pytest.raises(ValueError):
        is_dataframe_empty(empty_csv_to_dataframe)


def test_not_empty_data_frame(valid_csv_to_dataframe):
    assert is_dataframe_empty(valid_csv_to_dataframe) is False


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


def test_valid_csv_metadata(valid_csv_to_dataframe):
    assert is_csv_metadata_valid(valid_csv_to_dataframe) is True


def test_invalid_csv_metadata(empty_csv_to_dataframe):
    with pytest.raises(ValueError):
        is_csv_metadata_valid(empty_csv_to_dataframe)


def test_no_school_column(no_school_name_fixture):
    with pytest.raises(ValueError):
        is_csv_content_valid(no_school_name_fixture)


def test_no_unidadeAluno(no_unidadeAluno_fixture):
    with pytest.raises(ValueError):
        is_csv_content_valid(no_unidadeAluno_fixture)


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













