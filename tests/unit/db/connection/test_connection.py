"""Tests for database connection handling with the new connector architecture."""

from unittest.mock import MagicMock, patch

import mysql.connector
import psycopg2
import pytest
import logging

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factory import DatabaseFactory
from supabase_pydantic.db.models import PostgresConnectionParams, MySQLConnectionParams
from supabase_pydantic.db.connectors.postgres.connector import PostgresConnector
from supabase_pydantic.db.connectors.mysql.connector import MySQLConnector


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


@pytest.fixture
def mock_mysql_connector(monkeypatch):
    """Mock mysql.connector's connect method."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('row1',), ('row2',)]
    mock_mysql = MagicMock(return_value=mock_conn)
    monkeypatch.setattr('mysql.connector.connect', mock_mysql)
    return mock_mysql, mock_conn, mock_cursor


@pytest.fixture
def mock_postgres_connector():
    """Mock PostgresConnector instance."""
    mock_connector = MagicMock()
    mock_connector.__enter__.return_value = MagicMock()
    mock_connector.execute_query.return_value = [('row1',), ('row2',)]
    return mock_connector


@pytest.fixture
def mock_mysql_connector_instance():
    """Mock MySQLConnector instance."""
    mock_connector = MagicMock()
    mock_connector.__enter__.return_value = MagicMock()
    mock_connector.execute_query.return_value = [('row1',), ('row2',)]
    return mock_connector


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_create_postgres_connector(mock_psycopg2):
    """Test creating a PostgreSQL connector with connection parameters."""
    mock_connect, mock_conn, _ = mock_psycopg2
    # Mock the connector class itself
    with patch('supabase_pydantic.db.connectors.postgres.connector.PostgresConnector') as mock_connector_class:
        mock_connector_instance = MagicMock()
        mock_connector_class.return_value = mock_connector_instance
        # Mock the DatabaseFactory to return our mocked connector
        with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
            mock_registry.get.return_value = mock_connector_class
            # Create params and test connector creation
            params = PostgresConnectionParams(
                dbname='dbname', user='user', password='password', host='host', port='5432'
            )
            connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params=params)
            # Verify the connector was created with our params
            mock_connector_class.assert_called_once()
            assert connector is mock_connector_instance


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_postgres_connector_operational_error():
    """Test that PostgreSQL OperationalError is caught and re-raised as ConnectionError."""
    error_message = 'unable to connect to the database'
    # Mock the psycopg2.connect function
    with patch(
        'psycopg2.connect',
        side_effect=psycopg2.OperationalError(error_message),
    ):
        with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
            # Return the real PostgresConnector class
            mock_registry.get.return_value = PostgresConnector
            params = PostgresConnectionParams(
                dbname='mydb', user='user', password='pass', host='localhost', port='5432'
            )
            with pytest.raises(ConnectionError) as exc_info:
                connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params=params)
                with connector:
                    pass  # Connection will fail during context manager entry
            assert error_message in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_create_postgres_connector_from_db_url(mock_psycopg2):
    """Test creating a PostgreSQL connector from a database URL."""
    mock_connect, mock_conn, _ = mock_psycopg2
    # Mock the connector class
    with patch('supabase_pydantic.db.connectors.postgres.connector.PostgresConnector') as mock_connector_class:
        mock_connector_instance = MagicMock()
        mock_connector_class.return_value = mock_connector_instance
        # Mock the DatabaseFactory
        with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
            mock_registry.get.return_value = mock_connector_class
            # Create connector with URL
            db_url = 'postgresql://user:password@localhost:5432/dbname'
            connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params={'db_url': db_url})
            # Verify the connector was created
            mock_connector_class.assert_called_once()
            assert connector is mock_connector_instance


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_postgres_connector_check_connection_open(mock_psycopg2):
    """Test that PostgresConnector.check_connection returns True when connection is open."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = False
    with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
        # Use real PostgresConnector for this test
        mock_registry.get.return_value = PostgresConnector
        connector = DatabaseFactory.create_connector(
            DatabaseType.POSTGRES,
            connection_params=PostgresConnectionParams(
                dbname='dbname', user='user', password='pass', host='host', port='5432'
            ),
        )
        # Override the internal connection with our mock
        connector._conn = mock_conn
        # Test the check_connection method
        assert connector.check_connection(mock_conn) is True


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_postgres_connector_check_connection_closed(mock_psycopg2):
    """Test that PostgresConnector.check_connection returns False when connection is closed."""
    mock_conn = mock_psycopg2[1]
    mock_conn.closed = True
    with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
        # Use real PostgresConnector for this test
        mock_registry.get.return_value = PostgresConnector
        connector = DatabaseFactory.create_connector(
            DatabaseType.POSTGRES,
            connection_params=PostgresConnectionParams(
                dbname='dbname', user='user', password='pass', host='host', port='5432'
            ),
        )
        # Override the internal connection with our mock
        connector._conn = mock_conn
        # Test the check_connection method
        assert connector.check_connection(mock_conn) is False


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_postgres_connector_execute_query_success(mock_psycopg2):
    """Test that PostgresConnector.execute_query successfully retrieves results."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
        # Use real PostgresConnector for this test
        mock_registry.get.return_value = PostgresConnector
        connector = DatabaseFactory.create_connector(
            DatabaseType.POSTGRES,
            connection_params=PostgresConnectionParams(
                dbname='dbname', user='user', password='pass', host='host', port='5432'
            ),
        )
        # Test the execute_query method
        result = connector.execute_query(mock_conn, 'SELECT * FROM table;')
        mock_cursor.execute.assert_called_once_with('SELECT * FROM table;', ())
        mock_cursor.fetchall.assert_called_once()
        assert result == [('row1',), ('row2',)]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_postgres_connector_execute_query_failure(mock_psycopg2):
    """Test that PostgresConnector.execute_query handles exceptions properly."""
    mock_conn, mock_cursor = mock_psycopg2[1], mock_psycopg2[2]
    mock_cursor.execute.side_effect = Exception('Query failed')
    with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
        # Use real PostgresConnector for this test
        mock_registry.get.return_value = PostgresConnector
        connector = DatabaseFactory.create_connector(
            DatabaseType.POSTGRES,
            connection_params=PostgresConnectionParams(
                dbname='dbname', user='user', password='pass', host='host', port='5432'
            ),
        )
        # Test the execute_query method with failing query
        with pytest.raises(Exception) as exc_info:
            connector.execute_query(mock_conn, 'BAD QUERY')
        assert str(exc_info.value) == 'Query failed'


# MySQL specific tests
@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_create_mysql_connector(mock_mysql_connector):
    """Test creating a MySQL connector with connection parameters."""
    mock_connect, mock_conn, _ = mock_mysql_connector
    # Mock the connector class itself
    with patch('supabase_pydantic.db.connectors.mysql.connector.MySQLConnector') as mock_connector_class:
        mock_connector_instance = MagicMock()
        mock_connector_class.return_value = mock_connector_instance
        # Mock the DatabaseFactory to return our mocked connector
        with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
            mock_registry.get.return_value = mock_connector_class
            # Create params and test connector creation
            params = MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
            connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params=params)
            # Verify the connector was created with our params
            mock_connector_class.assert_called_once()
            assert connector is mock_connector_instance


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.connection
def test_mysql_connector_operational_error():
    """Test that MySQL OperationalError is handled properly in normal and debug modes."""
    error_message = 'unable to connect to the database'
    # Mock the mysql.connector.connect function
    with patch(
        'mysql.connector.connect',
        side_effect=mysql.connector.Error(error_message),
    ):
        with patch('supabase_pydantic.db.factory.DatabaseFactory._connector_registry') as mock_registry:
            # Return the real MySQLConnector class
            mock_registry.get.return_value = MySQLConnector

            # 1. Test normal mode (no exception should be raised)
            params = MySQLConnectionParams(
                dbname='testdb', user='root', password='mysql', host='localhost', port='3306'
            )
            # Should not raise ConnectionError in normal mode
            connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params=params)

            # 2. Test debug mode (exception should be raised)
            # Set logger level to DEBUG by patching the getEffectiveLevel method
            with patch(
                'supabase_pydantic.db.connectors.mysql.connector.logger.getEffectiveLevel', return_value=logging.DEBUG
            ):
                with pytest.raises(ConnectionError) as exc_info:
                    connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params=params)
                    with connector:
                        pass  # Connection will fail during context manager entry
                assert error_message in str(exc_info.value)
