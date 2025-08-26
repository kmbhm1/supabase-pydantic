"""Tests for MySQL connector implementation."""

from unittest.mock import MagicMock, patch

import pytest

from supabase_pydantic.db.models import MySQLConnectionParams
from supabase_pydantic.db.connectors.mysql.connector import MySQLConnector


@pytest.fixture
def mock_mysql_connect(monkeypatch):
    """Mock mysql.connector.connect method."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
    mock_mysql = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('mysql.connector.connect', mock_mysql)
    return mock_mysql, mock_conn, mock_cursor


@pytest.mark.unit
@pytest.mark.db
class TestMySQLConnector:
    """Test cases for the MySQL connector implementation."""

    def test_get_url_connection_params_valid_url(self):
        """Test parsing a valid MySQL connection URL."""
        connector = MySQLConnector()
        url = 'mysql://user:password@localhost:3306/testdb'
        params = connector.get_url_connection_params(url)

        # Check that URL is correctly parsed
        assert params['user'] == 'user'
        assert params['password'] == 'password'
        assert params['host'] == 'localhost'
        assert params['port'] == 3306
        assert params['database'] == 'testdb'

    def test_get_url_connection_params_with_encoded_password(self):
        """Test parsing a MySQL URL with special characters in password."""
        connector = MySQLConnector()
        url = 'mysql://user:pass%40word@localhost:3306/testdb'
        params = connector.get_url_connection_params(url)

        # Check that URL is correctly parsed with decoded password
        assert params['user'] == 'user'
        assert params['password'] == 'pass@word'
        assert params['host'] == 'localhost'
        assert params['port'] == 3306
        assert params['database'] == 'testdb'

    def test_get_url_connection_params_default_port(self):
        """Test that default port is used when not specified in URL."""
        connector = MySQLConnector()
        url = 'mysql://user:password@localhost/testdb'
        params = connector.get_url_connection_params(url)

        assert params['port'] == 3306  # Default MySQL port

    def test_get_url_connection_params_invalid_scheme(self):
        """Test that invalid scheme raises ValueError."""
        connector = MySQLConnector()
        url = 'postgresql://user:password@localhost:5432/testdb'

        with pytest.raises(ValueError) as exc_info:
            connector.get_url_connection_params(url)

        assert 'Invalid URL scheme' in str(exc_info.value)

    def test_validate_connection_params_with_url(self):
        """Test validating connection parameters with a database URL."""
        connector = MySQLConnector()

        # Mock get_url_connection_params to return known values
        with patch.object(connector, 'get_url_connection_params') as mock_get_params:
            mock_get_params.return_value = {
                'user': 'user',
                'password': 'password',
                'host': 'localhost',
                'port': 3306,
                'database': 'testdb',
            }

            params = {'db_url': 'mysql://user:password@localhost:3306/testdb'}
            validated_params = connector.validate_connection_params(params)

            # Verify the method was called with our URL
            mock_get_params.assert_called_once_with(params['db_url'])

            # Verify the validated parameters are correct
            assert validated_params.user == 'user'
            assert validated_params.password == 'password'
            assert validated_params.host == 'localhost'
            assert validated_params.port == '3306'  # Note: port is a string in the Pydantic model
            assert validated_params.dbname == 'testdb'

    def test_validate_connection_params_direct(self):
        """Test validating direct connection parameters."""
        connector = MySQLConnector()
        params = {'user': 'user', 'password': 'password', 'host': 'localhost', 'port': '3306', 'dbname': 'testdb'}

        validated_params = connector.validate_connection_params(params)

        assert validated_params.user == 'user'
        assert validated_params.password == 'password'
        assert validated_params.host == 'localhost'
        assert validated_params.port == '3306'
        assert validated_params.dbname == 'testdb'

    def test_validate_connection_params_missing_required(self):
        """Test that validation fails when required parameters are missing."""
        connector = MySQLConnector()
        params = {
            'password': 'password',
            'dbname': 'testdb',
            # Missing 'user' and 'host'
        }

        with pytest.raises(ValueError) as exc_info:
            connector.validate_connection_params(params)

        assert 'Missing required connection parameters' in str(exc_info.value)
        assert 'user' in str(exc_info.value)
        assert 'host' in str(exc_info.value)

    def test_validate_connection_params_pydantic_model(self):
        """Test that validating a Pydantic model returns the same model."""
        connector = MySQLConnector()
        model_params = MySQLConnectionParams(
            user='user', password='password', host='localhost', port='3306', dbname='testdb'
        )

        validated_params = connector.validate_connection_params(model_params)

        assert validated_params == model_params

    def test_context_manager_enter_exit(self, mock_mysql_connect):
        """Test the connector as a context manager."""
        mock_connect_fn, mock_conn, _ = mock_mysql_connect

        # Create connector with connection parameters
        connector = MySQLConnector(
            connection_params=MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
        )

        # Use connector as a context manager
        with connector as conn:
            assert conn is mock_conn  # __enter__ should return the connection
            mock_connect_fn.assert_called_once()  # connect() should be called once

        # After context exit, close_connection should have been called
        mock_conn.close.assert_called_once()

    def test_context_manager_with_exception(self, mock_mysql_connect):
        """Test the context manager when an exception occurs inside the context."""
        _, mock_conn, _ = mock_mysql_connect

        connector = MySQLConnector(
            connection_params=MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
        )

        # Simulate an exception inside the context manager
        with pytest.raises(ValueError):
            with connector as conn:
                assert conn is mock_conn
                raise ValueError('Test exception')

        # Connection should still be closed even when exception occurs
        mock_conn.close.assert_called_once()

    def test_context_manager_callable_style(self, mock_mysql_connect):
        """Test the connector using the callable style context manager."""
        mock_connect_fn, mock_conn, _ = mock_mysql_connect

        connector = MySQLConnector(
            connection_params=MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
        )

        # Use the callable style context manager
        with connector() as conn:
            assert conn is mock_conn
            mock_connect_fn.assert_called_once()

        # After context exit, close_connection should have been called
        mock_conn.close.assert_called_once()

    def test_execute_query_success(self, mock_mysql_connect):
        """Test successful execution of a query."""
        _, mock_conn, mock_cursor = mock_mysql_connect

        # Configure the mock cursor's fetchall to return specific data
        expected_results = [('value1',), ('value2',)]
        mock_cursor.fetchall.return_value = expected_results

        connector = MySQLConnector()

        # Execute a test query
        query = 'SELECT * FROM test_table'
        params = ()
        results = connector.execute_query(mock_conn, query, params)

        # Verify query was executed with correct parameters
        mock_cursor.execute.assert_called_once_with(query, params)
        mock_cursor.fetchall.assert_called_once()

        # Verify results are returned correctly
        assert results == expected_results

        # Verify cursor was properly created and closed
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_query_with_parameters(self, mock_mysql_connect):
        """Test execution of a query with parameters."""
        _, mock_conn, mock_cursor = mock_mysql_connect

        connector = MySQLConnector()

        # Execute a query with parameters
        query = 'SELECT * FROM users WHERE id = %s AND status = %s'
        params = (1, 'active')
        connector.execute_query(mock_conn, query, params)

        # Verify query was executed with correct parameters
        mock_cursor.execute.assert_called_once_with(query, params)

    def test_execute_query_failure(self, mock_mysql_connect):
        """Test handling of query execution failure."""
        _, mock_conn, mock_cursor = mock_mysql_connect

        # Configure the mock cursor to raise an exception on execute
        error_message = 'Query execution failed'
        mock_cursor.execute.side_effect = Exception(error_message)

        connector = MySQLConnector()

        # Execute a query that will fail
        query = 'INVALID SQL'

        # Verify the exception is propagated
        with pytest.raises(Exception) as exc_info:
            connector.execute_query(mock_conn, query, ())

        assert str(exc_info.value) == error_message

        # Verify cursor was properly created and closed even with error
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_check_connection_success(self, mock_mysql_connect):
        """Test successful connection check."""
        mock_connect_fn, mock_conn, mock_cursor = mock_mysql_connect

        # Configure mock to indicate successful connection
        mock_cursor.fetchone.return_value = (1,)

        connector = MySQLConnector(
            connection_params=MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
        )

        # Check connection - should create a new connection
        result = connector.check_connection()

        # Verify connection check was successful
        assert result is True

        # Verify that connect was called and "SELECT 1" was executed
        mock_connect_fn.assert_called_once()
        mock_cursor.execute.assert_called_once_with('SELECT 1')

        # Verify connection was closed after checking
        mock_conn.close.assert_called_once()

    def test_check_connection_failure(self):
        """Test failed connection check when connect raises an exception."""
        connector = MySQLConnector(
            connection_params=MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
        )

        # Mock the connect method to raise an exception
        with patch.object(connector, 'connect', side_effect=Exception('Connection failed')):
            # Check connection - should return False due to exception
            result = connector.check_connection()

            # Verify connection check failed
            assert result is False
