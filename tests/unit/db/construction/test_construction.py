"""Tests for database schema construction in supabase_pydantic.db.connection."""

from unittest.mock import MagicMock

import pytest

from supabase_pydantic.db.constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING,
    GET_CONSTRAINTS,
    GET_ENUM_TYPES,
    GET_TABLE_COLUMN_DETAILS,
    SCHEMAS_QUERY,
    DatabaseConnectionType,
)
from supabase_pydantic.db.connection import construct_tables


@pytest.fixture
def mock_database(monkeypatch):
    """Mocks all database interactions."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.side_effect = [
        [('table1', 'column1', 'type1')],  # Simulated response for table and column details
        [('table1', 'column1', 'fk_table1', 'fk_column1')],  # Simulated foreign key details
        [('constraint1', 'type1', 'details1')],  # Simulated constraints details
        [('table1', 'column1', 'enum1')],  # Simulated response for enum types
        [('table1', 'column1', 'enum1', 'enum2')],  # Simulated response for enum type mapping to columns
    ]
    mock_create_conn = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('supabase_pydantic.db.connection.create_connection', mock_create_conn)
    mock_check_conn = MagicMock(return_value=True)
    monkeypatch.setattr('supabase_pydantic.db.connection.check_connection', mock_check_conn)
    return mock_create_conn, mock_conn, mock_cursor


@pytest.fixture
def mock_construct_table_info(monkeypatch):
    # Mock construct_table_info and configure a return value
    mock_function = MagicMock(return_value={'info': 'sample data'})
    monkeypatch.setattr('supabase_pydantic.db.connection.construct_table_info', mock_function)
    return mock_function


@pytest.fixture
def mock_query_database(monkeypatch):
    def mock_query(conn, query, params=()):
        if query == SCHEMAS_QUERY:
            return [('public',)]
        elif query == GET_ALL_PUBLIC_TABLES_AND_COLUMNS:
            return [('column1', 'column2')]
        elif query == GET_TABLE_COLUMN_DETAILS:
            return [('fk_column1', 'fk_column2')]
        elif query == GET_CONSTRAINTS:
            return [('constraint1', 'constraint2')]
        elif query == GET_ENUM_TYPES:
            return [('enum1', 'enum2')]
        elif query == GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING:
            return [('mapping1', 'mapping2')]
        return []

    monkeypatch.setattr('supabase_pydantic.db.connection.query_database', mock_query)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.construction
def test_construct_tables_local_success(mock_database, mock_query_database, mock_construct_table_info):
    """Test successful construction of tables."""
    db_name, user, password, host, port = 'testdb', 'user', 'password', 'localhost', 5432
    result = construct_tables(
        DatabaseConnectionType.LOCAL,
        schemas=('public',),
        **{
            'DB_NAME': db_name,
            'DB_USER': user,
            'DB_PASS': password,
            'DB_HOST': host,
            'DB_PORT': port,
        },
    )
    assert 'public' in result
    assert result['public'] == {'info': 'sample data'}
    mock_construct_table_info.assert_called_once()  # Optionally check it was called correctly


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.construction
def test_construct_tables_local_failure(mock_database):
    """Test failure due to invalid connection parameters."""
    with pytest.raises(AssertionError):
        construct_tables(DatabaseConnectionType.LOCAL)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.construction
def test_construct_tables_db_url_success(mock_database, mock_query_database, mock_construct_table_info):
    """Test successful construction of tables."""
    db_url = 'postgresql://user:password@localhost:5432/testdb'
    result = construct_tables(DatabaseConnectionType.DB_URL, schemas=('public',), DB_URL=db_url)
    assert 'public' in result
    assert result['public'] == {'info': 'sample data'}
    mock_construct_table_info.assert_called_once()  # Optionally check it was called correctly


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.construction
def test_construct_tables_db_url_failure(mock_database):
    """Test failure due to invalid connection parameters."""
    with pytest.raises(AssertionError):
        construct_tables(DatabaseConnectionType.DB_URL)


@pytest.fixture
def mock_construct_table_info_raises_exception(monkeypatch):
    # Mock construct_table_info and configure it to raise an exception
    mock_function = MagicMock(side_effect=Exception('Failed to construct table info'))
    monkeypatch.setattr('supabase_pydantic.db.marshalers.schema.construct_table_info', mock_function)
    return mock_function


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.construction
def test_construct_tables_exception(mock_database, mock_query_database, mock_construct_table_info_raises_exception):
    """Test that construct_tables handles exceptions when constructing table info."""
    db_name, user, password, host, port = 'test', 'user', 'password', 'localhost', 5432
    with pytest.raises(Exception):
        construct_tables(
            DatabaseConnectionType.LOCAL,
            schemas=('public',),
            **{
                'DB_NAME': db_name,
                'DB_USER': user,
                'DB_PASS': password,
                'DB_HOST': host,
                'DB_PORT': port,
            },
        )
