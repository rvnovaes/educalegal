import pytest
import os

script_dir = os.path.dirname(__file__)

from web.util.file_import import *


@pytest.fixture
def valid_csv():
    with open(os.path.join(script_dir, "test_file_import_data_sources/valid.csv")) as csvfile:
        valid_data = pd.read_csv(csvfile, sep="#")
    return valid_data


@pytest.fixture
def only_headers():
    with open(os.path.join(script_dir, "test_file_import_data_sources/only_headers.csv")) as csvfile:
        empty = pd.read_csv(csvfile, sep="#")
    return empty


@pytest.fixture
def empty_content():
    with open(os.path.join(script_dir, "test_file_import_data_sources/empty_content.csv")) as csvfile:
        empty_content_fixture = pd.read_csv(csvfile, sep="#")
    return empty_content_fixture


@pytest.fixture
def metadata_fixture():
    with open(os.path.join(script_dir,
                           "test_file_import_data_sources/metadata_fixture.csv")) as csvfile:
        metadata_fixture = pd.read_csv(csvfile, sep="#")
    return metadata_fixture


@pytest.fixture
def no_school_name():
    with open(os.path.join(script_dir,
                           "test_file_import_data_sources/no_school_name_columnn.csv")) as csvfile:
        no_school_name_fixture = pd.read_csv(csvfile, sep="#")
    return no_school_name_fixture

@pytest.fixture
def no_unidadeAluno():
    with open(os.path.join(script_dir,
                           "test_file_import_data_sources/no_unidadeAluno_column.csv")) as csvfile:
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


@pytest.mark.parametrize('column_name, row_index, field_type_name, field_required, value, fails', [
    # Test CpfField
    ('cpf', 3, 'CpfField', True, '099.264.116-06', False),
    ('cpf', 5, 'CpfField', False, None, False),
    ('cpf', 7, 'CpfField', True, '099.264.116-05', True),
    ('cpf', 9, 'CpfField', True, '99.264.116-06', True),
    ('cpf', 11, 'CpfField', True, '0099.264.116.06', True),
    ('cpf', 13, 'CpfField', True, '09926411606', True),
    ('cpf', 15, 'CpfField', True, 99264116066, True),
    ('cpf', 17, 'CpfField', True, '333.333.333-33', True),
    ('cpf', 19, 'CpfField', True, 'not-an-cpf', True),
    ('cpf', 21, 'CpfField', True, '', True),
    ('cpf', 23, 'CpfField', True, None, True),
    ('cpf', 25, 'CpfField', False, '', True),
    ('cpf', 27, 'CpfField', False, ' ', True),
    # Test CnpjField
    ('cnpj', 3, 'CnpjField', True, '33.000.167/0001-01', False),
    ('cnpj', 5, 'CnpjField', False, None, False),
    ('cnpj', 7, 'CnpjField', True, '33.000.167/0001-10', True),
    ('cnpj', 9, 'CnpjField', True, '3.000.167/0001-01', True),
    ('cnpj', 11, 'CnpjField', True, '133.000.167/0001-01', True),
    ('cnpj', 13, 'CnpjField', True, '33000167000101', True),
    ('cnpj', 15, 'CnpjField', True, 33000167000101, True),
    ('cnpj', 17, 'CnpjField', True, '11.111.111/1111-11', True),
    ('cnpj', 19, 'CnpjField', True, 'not-an-cnpj', True),
    ('cnpj', 21, 'CnpjField', True, '', True),
    ('cnpj', 23, 'CnpjField', True, None, True),
    ('cnpj', 25, 'CnpjField', False, '', True),
    ('cnpj', 27, 'CnpjField', False, ' ', True),

])
def test_validate_field(column_name, row_index, field_type_name, field_required, value, fails):
    if not fails:
        expects = value, not fails
        result = validate_field(column_name, row_index, field_type_name, field_required, value)
        assert result == expects
    else:
        with pytest.raises(ValueError):
            validate_field(column_name, row_index, field_type_name, field_required, value)
