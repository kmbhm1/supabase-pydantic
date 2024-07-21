import pytest
from unittest.mock import MagicMock
from supabase_pydantic.util.db import (
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
    from psycopg2 import connect

    conn = create_connection('dbname', 'user', 'password', 'host', '5432')
    connect.assert_called_once_with(dbname='dbname', user='user', password='password', host='host', port='5432')
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
