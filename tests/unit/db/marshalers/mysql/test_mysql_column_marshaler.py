"""Tests for MySQL column marshaler implementation."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.marshalers.mysql.column import MySQLColumnMarshaler


@pytest.fixture
def marshaler():
    """Fixture to create a MySQLColumnMarshaler instance."""
    return MySQLColumnMarshaler()


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'field_int'),  # Reserved keyword
        ('print', 'field_print'),  # Built-in name
        ('model_abc', 'field_model_abc'),  # Starts with 'model_'
        ('username', 'username'),  # Not reserved
        ('id', 'id'),  # Exception, should not be modified
        ('credits', 'credits'),  # Business term exception
    ],
)
def test_standardize_column_name(marshaler, column_name, expected):
    """Test MySQL column name standardization."""
    result = marshaler.standardize_column_name(column_name)
    assert result == expected, f'Failed for {column_name}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, disable_protection, expected',
    [
        ('int', False, 'field_int'),
        ('model_abc', False, 'field_model_abc'),  # Normal case with protection
        ('model_abc', True, 'model_abc'),  # With protection disabled
        ('regular_column', True, 'regular_column'),
    ],
)
def test_standardize_column_name_with_protection_flag(marshaler, column_name, disable_protection, expected):
    """Test MySQL column name standardization with protection flag."""
    result = marshaler.standardize_column_name(column_name, disable_protection)
    assert result == expected, f'Failed for {column_name} with protection={disable_protection}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'int'),  # Reserved keyword
        ('model_name', 'model_name'),  # Starts with 'model_'
        ('id', ''),  # Exception, but MySQL marshaler returns empty string for None
        ('username', ''),  # Not reserved, returns empty string for None
    ],
)
def test_get_alias(marshaler, column_name, expected):
    """Test getting column aliases in MySQL."""
    result = marshaler.get_alias(column_name)
    assert result == expected, f'Failed for {column_name}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'db_type, type_info, expected',
    [
        ('int', 'int', 'int'),
        ('varchar', 'varchar', 'str'),
        ('text', 'text', 'str'),
        ('datetime', 'datetime', 'datetime'),
        ('float', 'float', 'float'),
        ('decimal', 'decimal', 'Decimal'),
        ('boolean', 'boolean', 'bool'),
        # Add more MySQL types as needed
    ],
)
@patch('supabase_pydantic.db.marshalers.mysql.column.process_udt_field')
def test_process_column_type(mock_process_udt, marshaler, db_type, type_info, expected):
    """Test processing column types for MySQL."""
    # Set up mock to return our expected value
    mock_process_udt.return_value = expected

    result = marshaler.process_column_type(db_type, type_info)

    # Verify process_udt_field was called with correct parameters
    mock_process_udt.assert_called_once_with(type_info, db_type, db_type=DatabaseType.MYSQL, known_enum_types=None)
    assert result == expected, f'Failed for {db_type}/{type_info}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_column_type_none_handling(marshaler):
    """Test handling of None values in process_column_type."""
    with patch('supabase_pydantic.db.marshalers.mysql.column.process_udt_field', return_value=None):
        result = marshaler.process_column_type('unknown', 'unknown')
        assert result == '', 'Should return empty string when process_udt_field returns None'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'element_type, expected',
    [
        ('int', 'list[int]'),
        ('str', 'list[str]'),
        ('bool', 'list[bool]'),
        ('CustomType', 'list[CustomType]'),
    ],
)
def test_process_array_type(marshaler, element_type, expected):
    """Test processing array types for MySQL."""
    result = marshaler.process_array_type(element_type)
    assert result == expected, f'Failed for {element_type}, got {result}, expected {expected}'
