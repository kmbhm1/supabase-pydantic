import pytest
from psycopg2 import connect
from unittest.mock import MagicMock
from supabase_pydantic.util.db import (
    construct_table_info_from_postgres,
    create_connection,
    check_connection,
    query_database,
)


@pytest.fixture
def mock_psycopg2(monkeypatch):
    """Mock psycopg2's connect method."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
    mock_psycopg2 = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('psycopg2.connect', mock_psycopg2)
    return mock_psycopg2, mock_conn, mock_cursor


def test_create_connection(mock_psycopg2):
    """Test that create_connection correctly initializes a psycopg2 connection."""
    mock_connect, _, _ = mock_psycopg2
    conn = create_connection('dbname', 'user', 'password', 'host', '5432')
    mock_connect.assert_called_once_with(dbname='dbname', user='user', password='password', host='host', port='5432')
    assert conn is mock_psycopg2[1]


def test_check_connection_open(mock_psycopg2):
    """Test that check_connection returns True when the connection is open."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = False
    assert check_connection(mock_conn) == True


def test_check_connection_closed(mock_psycopg2):
    """Test that check_connection returns False when the connection is closed."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = True
    assert check_connection(mock_conn) == False


def test_query_database_success(mock_psycopg2):
    """Test querying the database successfully retrieves results."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    result = query_database(mock_conn, 'SELECT * FROM table;')
    mock_cursor.execute.assert_called_once_with('SELECT * FROM table;')
    mock_cursor.fetchall.assert_called_once()
    assert result == [('row1',), ('row2',)]


def test_query_database_failure(mock_psycopg2):
    """Test that query_database handles exceptions when failing to execute a query."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    mock_cursor.execute.side_effect = Exception('Query failed')
    with pytest.raises(Exception) as exc_info:
        query_database(mock_conn, 'BAD QUERY')
    assert str(exc_info.value) == 'Query failed'
    mock_cursor.close.assert_called_once()


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
    ]
    mock_create_conn = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('supabase_pydantic.util.db.create_connection', mock_create_conn)
    mock_check_conn = MagicMock(return_value=True)
    monkeypatch.setattr('supabase_pydantic.util.db.check_connection', mock_check_conn)
    return mock_create_conn, mock_conn, mock_cursor


@pytest.fixture
def mock_construct_table_info(monkeypatch):
    # Mock construct_table_info and configure a return value
    mock_function = MagicMock(return_value={'info': 'sample data'})
    monkeypatch.setattr('supabase_pydantic.util.db.construct_table_info', mock_function)
    return mock_function


def test_construct_table_info_from_postgres_success(mock_database, mock_construct_table_info):
    """Test successful construction of table info from PostgreSQL."""
    db_name, user, password, host, port = 'testdb', 'user', 'password', 'localhost', '5432'
    result = construct_table_info_from_postgres(db_name, user, password, host, port)
    assert result == {'info': 'sample data'}
    mock_construct_table_info.assert_called_once()  # Optionally check it was called correctly


def test_construct_table_info_from_postgres_failure(mock_database):
    """Test failure due to invalid connection parameters."""
    with pytest.raises(AssertionError):
        construct_table_info_from_postgres(None, None, None, None, None)


def test_construct_table_info_from_postgres_query_failure(mock_database):
    """Test handling of a query execution failure."""
    _, _, mock_cursor = mock_database
    mock_cursor.execute.side_effect = Exception('Query failed')
    with pytest.raises(Exception) as exc_info:
        construct_table_info_from_postgres('testdb', 'user', 'pass', 'localhost', '5432')
    assert 'Query failed' in str(exc_info.value)
