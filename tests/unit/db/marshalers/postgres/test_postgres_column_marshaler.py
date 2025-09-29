"""Tests for PostgreSQL column marshaler implementation."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.marshalers.postgres.column import PostgresColumnMarshaler


@pytest.fixture
def marshaler():
    """Fixture to create a PostgresColumnMarshaler instance."""
    return PostgresColumnMarshaler()


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
    """Test PostgreSQL column name standardization."""
    with patch('supabase_pydantic.db.marshalers.postgres.column.std_column_name', return_value=expected):
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
    """Test PostgreSQL column name standardization with protection flag."""
    with patch('supabase_pydantic.db.marshalers.postgres.column.std_column_name', return_value=expected):
        result = marshaler.standardize_column_name(column_name, disable_protection)
        assert result == expected, f'Failed for {column_name} with protection={disable_protection}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_standardize_column_name_returns_empty_string_for_none(marshaler):
    """Test standardize_column_name handles None values properly."""
    with patch('supabase_pydantic.db.marshalers.postgres.column.std_column_name', return_value=None):
        result = marshaler.standardize_column_name('any_column')
        assert result == '', 'Should return empty string when standardization returns None'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'int'),  # Reserved keyword
        ('model_name', 'model_name'),  # Starts with 'model_'
        ('id', ''),  # Exception, returns empty string for None
        ('username', ''),  # Not reserved, returns empty string for None
    ],
)
def test_get_alias(marshaler, column_name, expected):
    """Test getting column aliases in PostgreSQL."""
    with patch('supabase_pydantic.db.marshalers.column.get_alias', return_value=expected if expected else None):
        result = marshaler.get_alias(column_name)
        assert result == expected, f'Failed for {column_name}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_alias_returns_empty_string_for_none(marshaler):
    """Test get_alias handles None values properly."""
    with patch('supabase_pydantic.db.marshalers.column.get_alias', return_value=None):
        result = marshaler.get_alias('any_column')
        assert result == '', 'Should return empty string when alias is None'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'db_type, type_info, expected',
    [
        ('int', 'int', 'int'),
        ('varchar', 'varchar', 'str'),
        ('text', 'text', 'str'),
        ('timestamp', 'timestamp', 'datetime.datetime'),
        ('float', 'float', 'Decimal'),
        ('numeric', 'numeric', 'Decimal'),
        ('boolean', 'boolean', 'bool'),
        ('json', 'json', 'dict | list[dict] | list[Any] | Json'),
        ('jsonb', 'jsonb', 'dict | list[dict] | list[Any] | Json'),
        ('uuid', 'uuid', 'UUID4'),
        # Add more PostgreSQL types as needed
    ],
)
def test_process_column_type(marshaler, db_type, type_info, expected):
    """Test processing column types for PostgreSQL."""
    with patch(
        'supabase_pydantic.db.marshalers.column.process_udt_field',
        return_value=expected,
    ):
        result = marshaler.process_column_type(db_type, type_info)
        assert result == expected, f'Failed for {db_type}/{type_info}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_column_type_none_handling(marshaler):
    """Test handling of None values in process_column_type."""
    # Since we've updated the implementation to return empty string for None,
    # Let's make sure our fix works
    with patch('supabase_pydantic.db.marshalers.column.process_udt_field', return_value=None):
        result = marshaler.process_column_type('unknown', 'unknown', enum_types=[])
        assert result == '', f'Should return empty string when process_udt_field returns None, got "{result}" instead'


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
    """Test processing array types for PostgreSQL."""
    result = marshaler.process_array_type(element_type)
    assert result == expected, f'Failed for {element_type}, got {result}, expected {expected}'
