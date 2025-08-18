"""Tests for database connection handling in supabase_pydantic.db.connection."""

from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from supabase_pydantic.db.connection import (
    DBConnection,
    check_connection,
    create_connection,
    create_connection_from_db_url,
    query_database,
)
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.exceptions import ConnectionError


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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_create_connection(mock_psycopg2):
    """Test that create_connection correctly initializes a psycopg2 connection."""
    mock_connect, _, _ = mock_psycopg2
    conn = create_connection('dbname', 'user', 'password', 'host', '5432')
    mock_connect.assert_called_once_with(dbname='dbname', user='user', password='password', host='host', port='5432')
    assert conn is mock_psycopg2[1]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_create_connection_operational_error():
    """Test that OperationalError is caught and re-raised as ConnectionError."""
    error_message = 'unable to connect to the database'
    with patch('psycopg2.connect', side_effect=psycopg2.OperationalError(error_message)):
        with pytest.raises(ConnectionError) as exc_info:
            create_connection('mydb', 'user', 'pass', 'localhost', '5432')
        assert str(exc_info.value) == f'Error connecting to database: {error_message}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_create_connection_from_db_url(mock_psycopg2):
    """Test that create_connection_from_db_url correctly initializes a psycopg2 connection."""
    mock_connect, _, _ = mock_psycopg2
    conn = create_connection_from_db_url('postgresql://user:password@localhost:5432/dbname')
    mock_connect.assert_called_once_with(
        dbname='dbname', user='user', password='password', host='localhost', port='5432'
    )
    assert conn is mock_psycopg2[1]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_check_connection_open(mock_psycopg2):
    """Test that check_connection returns True when the connection is open."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = False
    assert check_connection(mock_conn) is True


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_check_connection_closed(mock_psycopg2):
    """Test that check_connection returns False when the connection is closed."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = True
    assert check_connection(mock_conn) is False


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_query_database_success(mock_psycopg2):
    """Test querying the database successfully retrieves results."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    result = query_database(mock_conn, 'SELECT * FROM table;')
    mock_cursor.execute.assert_called_once_with('SELECT * FROM table;', ())
    mock_cursor.fetchall.assert_called_once()
    assert result == [('row1',), ('row2',)]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_query_database_failure(mock_psycopg2):
    """Test that query_database handles exceptions when failing to execute a query."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    mock_cursor.execute.side_effect = Exception('Query failed')
    with pytest.raises(Exception) as exc_info:
        query_database(mock_conn, 'BAD QUERY')
    assert str(exc_info.value) == 'Query failed'
    mock_cursor.close.assert_called_once()


@pytest.fixture
def mock_create_connection(monkeypatch):
    mock_conn = MagicMock()
    mock_create_conn = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('supabase_pydantic.db.connection.create_connection', mock_create_conn)
    return mock_create_conn


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_DBConnection_create_connection(mock_create_connection):
    """Test that DBConnection.create_connection correctly initializes a psycopg2 connection."""
    # Raises value error with incorrect key (KeyError)
    with pytest.raises(ValueError):
        _ = DBConnection(
            DatabaseConnectionType.LOCAL,
            DB_NAM='dbname',
            DB_USER='user',
            DB_PASS='password',
            DB_HOST='host',
            DB_PORT=5432,
        )

    assert (
        DBConnection(
            DatabaseConnectionType.LOCAL,
            DB_NAME='dbname',
            DB_USER='user',
            DB_PASS='password',
            DB_HOST='host',
            DB_PORT=5432,
        ).conn
        is mock_create_connection.return_value
    )

    with pytest.raises(ValueError):
        DBConnection(1)
    with pytest.raises(AttributeError):
        DBConnection(DatabaseConnectionType.INVAID)

    assert (
        DBConnection(DatabaseConnectionType.DB_URL, DB_URL='postgresql://user:password@localhost:5432/dbname').conn
        is mock_create_connection.return_value
    )
