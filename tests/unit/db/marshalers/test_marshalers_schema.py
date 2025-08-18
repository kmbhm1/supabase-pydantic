"""Tests for schema marshaler functions in supabase_pydantic.db.marshalers.schema."""

from unittest.mock import MagicMock
import pytest

from supabase_pydantic.db.models import (
    ColumnInfo,
    TableInfo,
)
from supabase_pydantic.db.marshalers.schema import (
    get_enum_types,
    get_table_details_from_columns,
    get_user_type_mappings,
    add_user_defined_types_to_tables,
)


@pytest.fixture
def column_details():
    return [
        ('public', 'users', 'user_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE', None, 'uuid', None),
        ('public', 'users', 'email', None, 'YES', 'text', 255, 'BASE TABLE', None, 'text', None),
    ]


@pytest.fixture
def column_construct_test_details():
    return [
        ('public', 'users', 'user_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE', None, 'uuid', None),
        ('public', 'users', 'email', None, 'YES', 'text', 255, 'BASE TABLE', None, 'text', None),
        ('public', 'orders', 'order_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE', None, 'uuid', None),
        ('public', 'orders', 'user_id', None, 'YES', 'uuid', None, 'BASE TABLE', None, 'uuid', None),
    ]


@pytest.fixture
def constraints():
    return [('pk_users', 'users', ['user_id'], 'PRIMARY KEY', 'PRIMARY KEY (user_id)')]


@pytest.fixture
def identity_column_details():
    return [
        ('public', 'users', 'id', None, 'NO', 'integer', None, 'BASE TABLE', 'ALWAYS', 'int4', None),
        ('public', 'users', 'name', None, 'YES', 'text', 255, 'BASE TABLE', None, 'text', None),
    ]


@pytest.fixture
def mock_enum_types():
    return [
        ('type_name', 'public', 'owner', 'category_1', True, 'e', ['user1', 'user2']),
        ('type_name_1', 'public', 'owner', 'category_2', True, 'e', ['value3', 'value4']),
        ('type_name_1', 'public', 'owner', 'category_3', True, 'c', ['value5', 'value6']),
        ('type_name_1', 'private', 'owner', 'category_4', True, 'd', ['value7', 'value8']),
    ]


@pytest.fixture
def mock_enum_type_mapping():
    return [
        ('username', 'users', 'public', 'type_name', 'category_1', 'foo'),
        ('username', 'users', 'public', 'type_name', 'category_2', 'bar'),
        ('username', 'users', 'public', 'type_name_1', 'category_3', 'baz'),
        ('username', 'users', 'public', 'type_name_1', 'category_4', 'qux'),
        ('username', 'users', 'private', 'type_name_1', 'category_4', 'qux'),
    ]


@pytest.fixture
def mock_tables():
    return {
        ('public', 'test_table'): TableInfo(
            name='test_table',
            columns=[
                ColumnInfo(name='id', user_defined_values=None, post_gres_datatype='uuid', datatype='str'),
                ColumnInfo(name='type', user_defined_values=None, post_gres_datatype='user-defined', datatype='str'),
            ],
        )
    }


@pytest.fixture
def get_enum_types_mock(mocker):
    mock = mocker.patch('supabase_pydantic.db.marshalers.schema.get_enum_types')
    mock.return_value = [
        # Example enum values setup
        MagicMock(type_name='my_enum', enum_values=['A', 'B', 'C'])
    ]
    return mock


@pytest.fixture
def get_user_type_mappings_mock(mocker):
    mock = mocker.patch('supabase_pydantic.db.marshalers.schema.get_user_type_mappings')
    mock.return_value = [
        # Example user type mappings setup
        MagicMock(table_name='test_table', column_name='type', type_name='my_enum')
    ]
    return mock


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_table_details_from_columns(column_details):
    result = get_table_details_from_columns(column_details)
    assert ('public', 'users') in result
    table = result[('public', 'users')]
    assert len(table.columns) == 2
    assert table.columns[0].name == 'user_id'
    assert table.columns[1].datatype == 'str'  # Assuming mapping in PYDANTIC_TYPE_MAP


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_constraints_to_table_details(column_details, constraints):
    from supabase_pydantic.db.marshalers.schema import add_constraints_to_table_details

    tables = get_table_details_from_columns(column_details)
    add_constraints_to_table_details(tables, 'public', constraints)
    table = tables[('public', 'users')]
    assert len(table.constraints) == 1
    assert table.constraints[0].constraint_name == 'pk_users'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_identity_columns(identity_column_details):
    tables = get_table_details_from_columns(identity_column_details)
    table = tables[('public', 'users')]

    # Check that identity column is properly identified
    id_column = next(col for col in table.columns if col.name == 'id')
    assert id_column.is_identity is True

    # Check non-identity column
    name_column = next(col for col in table.columns if col.name == 'name')
    assert name_column.is_identity is False


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_enum_types(mock_enum_types):
    # Call the function
    enum_types = get_enum_types(mock_enum_types, 'public')

    # Assert the output
    assert len(enum_types) == 2
    assert any(et.type_name == 'type_name' for et in enum_types)
    assert any(et.type_name == 'type_name_1' for et in enum_types)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_user_type_mappings(mock_enum_type_mapping):
    # Call the function
    user_type_mappings = get_user_type_mappings(mock_enum_type_mapping, 'public')

    # Assert the output
    assert len(user_type_mappings) == 4
    assert user_type_mappings[0].type_category == 'category_1'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_user_defined_types_valid_input(
    mock_tables, mock_enum_types, mock_enum_type_mapping, get_enum_types_mock, get_user_type_mappings_mock
):
    add_user_defined_types_to_tables(mock_tables, 'public', mock_enum_types, mock_enum_type_mapping)
    assert mock_tables[('public', 'test_table')].columns[1].user_defined_values == [
        'A',
        'B',
        'C',
    ], 'Enum values should be assigned correctly'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_table_key_not_found(
    mock_tables, mock_enum_types, mock_enum_type_mapping, get_enum_types_mock, get_user_type_mappings_mock
):
    # Adjust the mapping to a non-existent table
    get_user_type_mappings_mock.return_value = [
        MagicMock(table_name='nonexistent_table', column_name='type', type_name='my_enum')
    ]

    # Test that calling the function with a non-existent table doesn't raise an exception
    add_user_defined_types_to_tables(mock_tables, 'public', mock_enum_types, mock_enum_type_mapping)

    # The function should not raise an exception and should continue execution
    assert True


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_column_name_not_found(
    mock_tables, mock_enum_types, mock_enum_type_mapping, get_enum_types_mock, get_user_type_mappings_mock
):
    # Adjust the mapping to a non-existent column
    get_user_type_mappings_mock.return_value = [
        MagicMock(table_name='test_table', column_name='nonexistent_column', type_name='my_enum')
    ]
    add_user_defined_types_to_tables(mock_tables, 'public', mock_enum_types, mock_enum_type_mapping)
    assert True, 'Should handle non-existent column gracefully'
