from unittest.mock import MagicMock, patch

import psycopg2
import pytest

from supabase_pydantic.util.constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING,
    GET_CONSTRAINTS,
    GET_ENUM_TYPES,
    GET_TABLE_COLUMN_DETAILS,
    SCHEMAS_QUERY,
    DatabaseConnectionType,
)
from supabase_pydantic.util.db import (
    DBConnection,
    check_connection,
    construct_tables,
    create_connection,
    create_connection_from_db_url,
    query_database,
)
from supabase_pydantic.util.exceptions import ConnectionError


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


def test_create_connection_operational_error():
    """Test that OperationalError is caught and re-raised as ConnectionError."""
    error_message = 'unable to connect to the database'
    with patch('psycopg2.connect', side_effect=psycopg2.OperationalError(error_message)):
        with pytest.raises(ConnectionError) as exc_info:
            create_connection('mydb', 'user', 'pass', 'localhost', '5432')
        assert str(exc_info.value) == f'Error connecting to database: {error_message}'


def test_create_connection_from_db_url(mock_psycopg2):
    """Test that create_connection_from_db_url correctly initializes a psycopg2 connection."""
    mock_connect, _, _ = mock_psycopg2
    conn = create_connection_from_db_url('postgresql://user:password@localhost:5432/dbname')
    mock_connect.assert_called_once_with(
        dbname='dbname', user='user', password='password', host='localhost', port='5432'
    )
    assert conn is mock_psycopg2[1]


def test_check_connection_open(mock_psycopg2):
    """Test that check_connection returns True when the connection is open."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = False
    assert check_connection(mock_conn) is True


def test_check_connection_closed(mock_psycopg2):
    """Test that check_connection returns False when the connection is closed."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = True
    assert check_connection(mock_conn) is False


def test_query_database_success(mock_psycopg2):
    """Test querying the database successfully retrieves results."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    result = query_database(mock_conn, 'SELECT * FROM table;')
    mock_cursor.execute.assert_called_once_with('SELECT * FROM table;', ())
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
        [('table1', 'column1', 'enum1')],  # Simulated response for enum types
        [('table1', 'column1', 'enum1', 'enum2')],  # Simulated response for enum type mapping to columns
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

    monkeypatch.setattr('supabase_pydantic.util.db.query_database', mock_query)


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


def test_construct_tables_local_failure(mock_database):
    """Test failure due to invalid connection parameters."""
    with pytest.raises(AssertionError):
        construct_tables(DatabaseConnectionType.LOCAL)


def test_construct_tables_db_url_success(mock_database, mock_query_database, mock_construct_table_info):
    """Test successful construction of tables."""
    db_url = 'postgresql://user:password@localhost:5432/testdb'
    result = construct_tables(DatabaseConnectionType.DB_URL, schemas=('public',), DB_URL=db_url)
    assert 'public' in result
    assert result['public'] == {'info': 'sample data'}
    mock_construct_table_info.assert_called_once()  # Optionally check it was called correctly


def test_construct_tables_db_url_failure(mock_database):
    """Test failure due to invalid connection parameters."""
    with pytest.raises(AssertionError):
        construct_tables(DatabaseConnectionType.DB_URL)


@pytest.fixture
def mock_construct_table_info_raises_exception(monkeypatch):
    # Mock construct_table_info and configure it to raise an exception
    mock_function = MagicMock(side_effect=Exception('Failed to construct table info'))
    monkeypatch.setattr('supabase_pydantic.util.db.construct_table_info', mock_function)
    return mock_function


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


@pytest.fixture
def mock_create_connection(monkeypatch):
    mock_conn = MagicMock()
    mock_create_conn = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('supabase_pydantic.util.db.create_connection', mock_create_conn)
    return mock_create_conn


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
