import pytest
import os

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
        is_field_type_metadata_valid("empty_type_name", metadata_fixture["empty_type_name"])
        is_field_type_metadata_valid("wrong_type_name", metadata_fixture["wrong_type_name"])


def test_boolean_flag_metadata(metadata_fixture):
    metadata_fixture = metadata_fixture.loc[1].to_dict()
    assert is_field_empty("valid_field", metadata_fixture["valid_field"]) is False
    assert is_boolean_flag_valid("valid_field", metadata_fixture["valid_field"]) is True
    with pytest.raises(ValueError):
        is_field_empty("empty_boolean_flag", metadata_fixture["empty_boolean_flag"])
        is_boolean_flag_valid("empty_boolean_flag", metadata_fixture["empty_boolean_flag"])
        is_boolean_flag_valid("wrong_boolean_flag", metadata_fixture["wrong_boolean_flag"])


def test_valid_csv_metadata(valid_csv_to_dataframe):
    assert is_csv_metadata_valid(valid_csv_to_dataframe) is True


def test_invalid_csv_metadata(empty_csv_to_dataframe):
    with pytest.raises(ValueError):
        is_csv_metadata_valid(empty_csv_to_dataframe)






