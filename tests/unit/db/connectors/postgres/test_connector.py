"""Tests for PostgresConnector implementation."""

import pytest
from unittest.mock import patch, Mock
import psycopg2

from supabase_pydantic.db.connectors.postgres.connector import PostgresConnector
from supabase_pydantic.db.models import PostgresConnectionParams


@pytest.fixture
def valid_connection_params():
    """Fixture for valid connection parameters."""
    return PostgresConnectionParams(
        dbname='testdb', user='testuser', password='testpass', host='localhost', port='5432'
    )


@pytest.fixture
def valid_connection_params_dict():
    """Fixture for valid connection parameters as dictionary."""
    return {
        'dbname': 'testdb',
        'user': 'testuser',
        'password': 'testpass',
        'host': 'localhost',
        'port': '5432',
    }


@pytest.fixture
def valid_connection_url():
    """Fixture for valid connection URL."""
    return 'postgresql://testuser:testpass@localhost:5432/testdb'


@pytest.fixture
def connector():
    """Fixture for PostgresConnector instance with no parameters."""
    return PostgresConnector()


@pytest.fixture
def connector_with_params(valid_connection_params):
    """Fixture for PostgresConnector instance with valid parameters."""
    return PostgresConnector(valid_connection_params)


@pytest.mark.unit
@pytest.mark.db
def test_init_no_params():
    """Test initialization with no parameters."""
    connector = PostgresConnector()
    assert connector.connection_params is None


@pytest.mark.unit
@pytest.mark.db
def test_init_with_params(valid_connection_params):
    """Test initialization with valid parameters."""
    connector = PostgresConnector(valid_connection_params)
    assert connector.connection_params == valid_connection_params


@pytest.mark.unit
@pytest.mark.db
def test_init_with_dict(valid_connection_params_dict):
    """Test initialization with valid parameters as dictionary."""
    connector = PostgresConnector(valid_connection_params_dict)
    # The connection_params should be converted to PostgresConnectionParams
    assert isinstance(connector.connection_params, PostgresConnectionParams)
    assert connector.connection_params.dbname == valid_connection_params_dict['dbname']
    assert connector.connection_params.user == valid_connection_params_dict['user']
    assert connector.connection_params.password == valid_connection_params_dict['password']
    assert connector.connection_params.host == valid_connection_params_dict['host']
    assert connector.connection_params.port == valid_connection_params_dict['port']


@pytest.mark.unit
@pytest.mark.db
def test_validate_connection_params_with_model(valid_connection_params):
    """Test validation of connection parameters with Pydantic model."""
    connector = PostgresConnector()
    validated = connector.validate_connection_params(valid_connection_params)
    assert validated == valid_connection_params


@pytest.mark.unit
@pytest.mark.db
def test_validate_connection_params_with_dict(valid_connection_params_dict):
    """Test validation of connection parameters with dictionary."""
    connector = PostgresConnector()
    validated = connector.validate_connection_params(valid_connection_params_dict)
    assert isinstance(validated, PostgresConnectionParams)
    assert validated.dbname == valid_connection_params_dict['dbname']
    assert validated.user == valid_connection_params_dict['user']
    assert validated.password == valid_connection_params_dict['password']
    assert validated.host == valid_connection_params_dict['host']
    assert validated.port == valid_connection_params_dict['port']


@pytest.mark.unit
@pytest.mark.db
def test_validate_connection_params_invalid_model():
    """Test validation of invalid connection parameters with Pydantic model."""
    connector = PostgresConnector()
    # Create an invalid params object (missing required fields)
    invalid_params = PostgresConnectionParams(host='localhost')  # Missing required fields

    # Test directly without patching - the is_valid method should return False
    # for this invalid configuration, raising ValueError from the connector
    with pytest.raises(ValueError):
        connector.validate_connection_params(invalid_params)


@pytest.mark.unit
@pytest.mark.db
def test_validate_connection_params_invalid_dict():
    """Test validation of invalid connection parameters with dictionary."""
    connector = PostgresConnector()
    invalid_params = {'host': 'localhost'}  # Missing required fields

    with pytest.raises(ValueError):
        connector.validate_connection_params(invalid_params)


@pytest.mark.unit
@pytest.mark.db
def test_get_url_connection_params(valid_connection_url, valid_connection_params_dict):
    """Test parsing connection URL into parameters."""
    connector = PostgresConnector()
    params = connector.get_url_connection_params(valid_connection_url)

    assert params['dbname'] == valid_connection_params_dict['dbname']
    assert params['user'] == valid_connection_params_dict['user']
    assert params['password'] == valid_connection_params_dict['password']
    assert params['host'] == valid_connection_params_dict['host']
    assert params['port'] == valid_connection_params_dict['port']


@pytest.mark.unit
@pytest.mark.db
def test_get_url_connection_params_invalid():
    """Test parsing invalid connection URL."""
    connector = PostgresConnector()

    # Missing username - urlparse returns None for username
    with pytest.raises(ValueError) as exc_info:
        connector.get_url_connection_params('postgresql://localhost:5432/testdb')
    assert 'Invalid database URL user' in str(exc_info.value)

    # Missing password - urlparse returns None for password
    with pytest.raises(ValueError) as exc_info:
        connector.get_url_connection_params('postgresql://testuser@localhost:5432/testdb')
    assert 'Invalid database URL password' in str(exc_info.value)

    # Missing host
    with pytest.raises(ValueError) as exc_info:
        connector.get_url_connection_params('postgresql://testuser:testpass@:5432/testdb')
    assert 'Invalid database URL host' in str(exc_info.value)

    # Missing port
    with pytest.raises(ValueError) as exc_info:
        connector.get_url_connection_params('postgresql://testuser:testpass@localhost/testdb')
    assert 'Invalid database URL port' in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.db
def test_connect_with_url(connector, valid_connection_url):
    """Test creating connection from URL."""
    # Mock the _create_connection_from_url method
    with patch.object(connector, '_create_connection_from_url') as mock_create:
        mock_conn = Mock()
        mock_create.return_value = mock_conn

        # Call connect with db_url
        conn = connector.connect(db_url=valid_connection_url)

        # Verify _create_connection_from_url was called with the URL
        mock_create.assert_called_once_with(valid_connection_url)
        assert conn == mock_conn


@pytest.mark.unit
@pytest.mark.db
def test_connect_with_direct_params(connector, valid_connection_params_dict):
    """Test creating connection with direct parameters."""
    # Mock the _create_connection method
    with patch.object(connector, '_create_connection') as mock_create:
        mock_conn = Mock()
        mock_create.return_value = mock_conn

        # Call connect with direct parameters
        conn = connector.connect(**valid_connection_params_dict)

        # Verify _create_connection was called with the correct parameters
        mock_create.assert_called_once_with(
            valid_connection_params_dict['dbname'],
            valid_connection_params_dict['user'],
            valid_connection_params_dict['password'],
            valid_connection_params_dict['host'],
            valid_connection_params_dict['port'],
        )
        assert conn == mock_conn


@pytest.mark.unit
@pytest.mark.db
def test_connect_with_stored_params(connector_with_params):
    """Test creating connection using stored parameters."""
    # Mock the _create_connection method
    with patch.object(connector_with_params, '_create_connection') as mock_create:
        mock_conn = Mock()
        mock_create.return_value = mock_conn

        # Call connect with no parameters - should use stored ones
        conn = connector_with_params.connect()

        # Verify _create_connection was called with stored parameters
        params = connector_with_params.connection_params
        mock_create.assert_called_once_with(params.dbname, params.user, params.password, params.host, params.port)
        assert conn == mock_conn


@pytest.mark.unit
@pytest.mark.db
def test_connect_invalid_params(connector):
    """Test connect with invalid parameters."""
    # Missing required parameters
    with pytest.raises(ValueError):
        connector.connect(dbname='testdb')  # Missing other required fields


@pytest.mark.unit
@pytest.mark.db
def test_create_connection(connector):
    """Test direct connection creation."""
    # Mock psycopg2.connect
    with patch('psycopg2.connect') as mock_connect:
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        # Call _create_connection
        conn = connector._create_connection('testdb', 'testuser', 'testpass', 'localhost', '5432')

        # Verify psycopg2.connect was called with correct parameters
        mock_connect.assert_called_once_with(
            dbname='testdb', user='testuser', password='testpass', host='localhost', port='5432'
        )
        assert conn == mock_conn


@pytest.mark.unit
@pytest.mark.db
def test_create_connection_error(connector):
    """Test handling of connection errors."""
    # Mock psycopg2.connect to raise an OperationalError
    with patch('psycopg2.connect', side_effect=psycopg2.OperationalError('connection failed')):
        # Call _create_connection and verify it raises ConnectionError
        with pytest.raises(ConnectionError) as exc_info:
            connector._create_connection('testdb', 'testuser', 'testpass', 'localhost', '5432')

        assert 'Error connecting to PostgreSQL database' in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.db
def test_create_connection_from_url(connector, valid_connection_url):
    """Test creating connection from URL."""
    # Mock get_url_connection_params and _create_connection
    params = {'dbname': 'testdb', 'user': 'testuser', 'password': 'testpass', 'host': 'localhost', 'port': '5432'}

    with (
        patch.object(connector, 'get_url_connection_params', return_value=params) as mock_get_params,
        patch.object(connector, '_create_connection') as mock_create,
    ):
        mock_conn = Mock()
        mock_create.return_value = mock_conn

        # Call _create_connection_from_url
        conn = connector._create_connection_from_url(valid_connection_url)

        # Verify methods were called correctly
        mock_get_params.assert_called_once_with(valid_connection_url)
        mock_create.assert_called_once_with(
            params['dbname'], params['user'], params['password'], params['host'], params['port']
        )
        assert conn == mock_conn


@pytest.mark.unit
@pytest.mark.db
def test_check_connection_with_provided_conn():
    """Test connection check with provided connection."""
    connector = PostgresConnector()

    # Test with open connection
    mock_conn = Mock()
    mock_conn.closed = False
    assert connector.check_connection(mock_conn) is True

    # Test with closed connection
    mock_conn.closed = True
    assert connector.check_connection(mock_conn) is False


@pytest.mark.unit
@pytest.mark.db
def test_check_connection_creates_temp_conn(connector):
    """Test connection check creates temporary connection."""
    # Mock connector.connect and close_connection
    with patch.object(connector, 'connect') as mock_connect, patch.object(connector, 'close_connection') as mock_close:
        mock_conn = Mock()
        mock_conn.closed = False
        mock_connect.return_value = mock_conn

        # Test with successful connection
        assert connector.check_connection() is True
        mock_connect.assert_called_once()
        mock_close.assert_called_once_with(mock_conn)


@pytest.mark.unit
@pytest.mark.db
def test_check_connection_handles_error(connector):
    """Test connection check handles connection errors."""
    # Mock connector.connect to raise an exception
    with patch.object(connector, 'connect', side_effect=ConnectionError('connection failed')):
        assert connector.check_connection() is False


@pytest.mark.unit
@pytest.mark.db
def test_execute_query():
    """Test query execution."""
    connector = PostgresConnector()

    # Create mock connection and cursor
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('row1',), ('row2',)]

    # Execute query
    result = connector.execute_query(mock_conn, 'SELECT * FROM test', ('param',))

    # Verify cursor methods were called correctly
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with('SELECT * FROM test', ('param',))
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert result == [('row1',), ('row2',)]


@pytest.mark.unit
@pytest.mark.db
def test_execute_query_non_list_result():
    """Test query execution with non-list result."""
    connector = PostgresConnector()

    # Create mock connection and cursor
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = None  # Non-list result

    # Execute query
    result = connector.execute_query(mock_conn, 'SELECT * FROM test')

    # Verify empty list is returned
    assert result == []


@pytest.mark.unit
@pytest.mark.db
def test_close_connection():
    """Test connection closing."""
    connector = PostgresConnector()

    # Create mock connection
    mock_conn = Mock()

    # Close connection
    connector.close_connection(mock_conn)

    # Verify close was called
    mock_conn.close.assert_called_once()
