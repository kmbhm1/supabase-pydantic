"""Tests for PostgreSQL schema reader implementation."""

import pytest
from unittest.mock import MagicMock, patch

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.connectors.postgres.schema_reader import PostgresSchemaReader
from supabase_pydantic.db.drivers.postgres.queries import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING,
    GET_CONSTRAINTS,
    GET_ENUM_TYPES,
    GET_TABLE_COLUMN_DETAILS,
    SCHEMAS_QUERY,
    TABLES_QUERY,
)


@pytest.fixture
def mock_connector():
    """Create a mock connector for testing."""
    connector = MagicMock(spec=BaseDBConnector)
    return connector


@pytest.fixture
def schema_reader(mock_connector):
    """Create a PostgresSchemaReader instance with a mock connector."""
    with patch('logging.getLogger'):  # Patch logger to avoid actual logging
        return PostgresSchemaReader(mock_connector)


@pytest.mark.unit
@pytest.mark.db
def test_init_logs_initialization(mock_connector):
    """Test that initialization logs a message."""
    with patch('supabase_pydantic.db.connectors.postgres.schema_reader.logger') as mock_logger:
        PostgresSchemaReader(mock_connector)

        mock_logger.info.assert_called_once_with('PostgresSchemaReader initialized - schema_reader.py is being used!')


@pytest.mark.unit
@pytest.mark.db
def test_get_schemas(schema_reader, mock_connector):
    """Test getting schemas from PostgreSQL."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = [('public',), ('schema2',)]

    # Call method
    result = schema_reader.get_schemas(mock_conn)

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, SCHEMAS_QUERY)

    # Verify result
    assert result == ['public', 'schema2']


@pytest.mark.unit
@pytest.mark.db
def test_get_tables(schema_reader, mock_connector):
    """Test getting tables from PostgreSQL schema."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    expected_result = [('table1', 'description1'), ('table2', 'description2')]
    mock_connector.execute_query.return_value = expected_result

    # Call method
    result = schema_reader.get_tables(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, TABLES_QUERY, ('public',))

    # Verify result
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.db
def test_get_tables_non_list_result(schema_reader, mock_connector):
    """Test handling of non-list result when getting tables."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = None

    # Call method
    result = schema_reader.get_tables(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, TABLES_QUERY, ('public',))

    # Verify result
    assert result == []


@pytest.mark.unit
@pytest.mark.db
def test_get_columns(schema_reader, mock_connector):
    """Test getting columns from PostgreSQL schema."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    expected_result = [
        ('table1', 'column1', 'int', False),
        ('table1', 'column2', 'varchar', True),
    ]
    mock_connector.execute_query.return_value = expected_result

    # Call method
    result = schema_reader.get_columns(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, GET_ALL_PUBLIC_TABLES_AND_COLUMNS, ('public',))

    # Verify result
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.db
def test_get_columns_non_list_result(schema_reader, mock_connector):
    """Test handling of non-list result when getting columns."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = None

    # Call method
    result = schema_reader.get_columns(mock_conn, 'public')

    # Verify result
    assert result == []


@pytest.mark.unit
@pytest.mark.db
def test_get_foreign_keys(schema_reader, mock_connector):
    """Test getting foreign keys from PostgreSQL schema."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    expected_result = [
        ('table1', 'column1', 'table2', 'id'),
        ('table3', 'column2', 'table4', 'id'),
    ]
    mock_connector.execute_query.return_value = expected_result

    # Call method
    result = schema_reader.get_foreign_keys(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, GET_TABLE_COLUMN_DETAILS, ('public',))

    # Verify result
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.db
def test_get_foreign_keys_non_list_result(schema_reader, mock_connector):
    """Test handling of non-list result when getting foreign keys."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = None

    # Call method
    result = schema_reader.get_foreign_keys(mock_conn, 'public')

    # Verify result
    assert result == []


@pytest.mark.unit
@pytest.mark.db
def test_get_constraints(schema_reader, mock_connector):
    """Test getting constraints from PostgreSQL schema."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    expected_result = [
        ('table1', 'pk_constraint', 'PRIMARY KEY'),
        ('table1', 'uq_constraint', 'UNIQUE'),
    ]
    mock_connector.execute_query.return_value = expected_result

    # Call method
    result = schema_reader.get_constraints(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, GET_CONSTRAINTS, ('public',))

    # Verify result
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.db
def test_get_constraints_non_list_result(schema_reader, mock_connector):
    """Test handling of non-list result when getting constraints."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = None

    # Call method
    result = schema_reader.get_constraints(mock_conn, 'public')

    # Verify result
    assert result == []


@pytest.mark.unit
@pytest.mark.db
def test_get_user_defined_types(schema_reader, mock_connector):
    """Test getting user-defined types from PostgreSQL schema."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    expected_result = [
        ('status_enum', 'ENUM', ['active', 'inactive', 'pending']),
        ('address_type', 'COMPOSITE', None),
    ]
    mock_connector.execute_query.return_value = expected_result

    # Call method
    result = schema_reader.get_user_defined_types(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(mock_conn, GET_ENUM_TYPES, ('public',))

    # Verify result
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.db
def test_get_user_defined_types_non_list_result(schema_reader, mock_connector):
    """Test handling of non-list result when getting user-defined types."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = None

    # Call method
    result = schema_reader.get_user_defined_types(mock_conn, 'public')

    # Verify result
    assert result == []


@pytest.mark.unit
@pytest.mark.db
def test_get_type_mappings(schema_reader, mock_connector):
    """Test getting type mappings from PostgreSQL schema."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    expected_result = [
        ('table1', 'column1', 'status_enum'),
        ('table2', 'column2', 'address_type'),
    ]
    mock_connector.execute_query.return_value = expected_result

    # Call method
    result = schema_reader.get_type_mappings(mock_conn, 'public')

    # Verify correct query was executed
    mock_connector.execute_query.assert_called_once_with(
        mock_conn, GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING, ('public',)
    )

    # Verify result
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.db
def test_get_type_mappings_non_list_result(schema_reader, mock_connector):
    """Test handling of non-list result when getting type mappings."""
    # Setup mock connection and query result
    mock_conn = MagicMock()
    mock_connector.execute_query.return_value = None

    # Call method
    result = schema_reader.get_type_mappings(mock_conn, 'public')

    # Verify result
    assert result == []
