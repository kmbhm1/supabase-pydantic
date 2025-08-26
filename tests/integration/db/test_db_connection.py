"""Integration tests for database connection functionality.

These tests require an actual database connection to run.
"""

import os

import pytest
from dotenv import load_dotenv

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.exceptions import ConnectionError
from supabase_pydantic.db.factory import DatabaseFactory
from supabase_pydantic.db.models import PostgresConnectionParams, MySQLConnectionParams


# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def postgres_params():
    """Get database connection parameters from environment variables."""
    return PostgresConnectionParams(
        dbname=os.environ.get('TEST_DB_NAME', 'postgres'),
        user=os.environ.get('TEST_DB_USER', 'postgres'),
        password=os.environ.get('TEST_DB_PASS', 'postgres'),
        host=os.environ.get('TEST_DB_HOST', 'localhost'),
        port=os.environ.get('TEST_DB_PORT', '5432'),
    )


@pytest.fixture
def postgres_url():
    """Get database URL from environment variables."""
    return os.environ.get(
        'TEST_DB_URL',
        'postgresql://postgres:postgres@localhost:5432/postgres',
    )


@pytest.fixture
def mysql_params():
    """Get MySQL database connection parameters from environment variables."""
    return MySQLConnectionParams(
        dbname=os.environ.get('TEST_MYSQL_DB_NAME', 'test'),
        user=os.environ.get('TEST_MYSQL_USER', 'root'),
        password=os.environ.get('TEST_MYSQL_PASS', 'mysql'),
        host=os.environ.get('TEST_MYSQL_HOST', 'localhost'),
        port=os.environ.get('TEST_MYSQL_PORT', '3306'),
    )


@pytest.fixture
def mysql_url():
    """Get MySQL database URL from environment variables."""
    return os.environ.get(
        'TEST_MYSQL_URL',
        'mysql://root:mysql@localhost:3306/test',
    )


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_create_connection_integration(postgres_params):
    """Test creating a database connection with actual credentials."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params=postgres_params)
        with connector as conn:
            assert conn is not None
            assert connector.check_connection(conn) is True
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS') or not os.environ.get('RUN_MYSQL_TESTS'),
    reason='MySQL database integration tests are disabled. Set both RUN_DB_TESTS=1 and RUN_MYSQL_TESTS=1 to enable.',
)
def test_create_mysql_connection_integration(mysql_params):
    """Test creating a MySQL database connection with actual credentials."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params=mysql_params)
        with connector as conn:
            assert conn is not None
            assert connector.check_connection(conn) is True
    except ConnectionError as e:
        pytest.skip(f'Could not connect to MySQL database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_create_connection_from_db_url_integration(postgres_url):
    """Test creating a database connection from a URL with actual credentials."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params={'db_url': postgres_url})
        with connector as conn:
            assert conn is not None
            assert connector.check_connection(conn) is True
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS') or not os.environ.get('RUN_MYSQL_TESTS'),
    reason='MySQL database integration tests are disabled. Set both RUN_DB_TESTS=1 and RUN_MYSQL_TESTS=1 to enable.',
)
def test_create_mysql_connection_from_db_url_integration(mysql_url):
    """Test creating a MySQL database connection from a URL with actual credentials."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params={'db_url': mysql_url})
        with connector as conn:
            assert conn is not None
            assert connector.check_connection(conn) is True
    except ConnectionError as e:
        pytest.skip(f'Could not connect to MySQL database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_query_database_integration(postgres_params):
    """Test querying the database with a simple query."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params=postgres_params)
        with connector as conn:
            results = connector.execute_query(conn, 'SELECT 1 AS test')
            assert results == [(1,)]
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS') or not os.environ.get('RUN_MYSQL_TESTS'),
    reason='MySQL database integration tests are disabled. Set both RUN_DB_TESTS=1 and RUN_MYSQL_TESTS=1 to enable.',
)
def test_mysql_query_database_integration(mysql_params):
    """Test querying the MySQL database with a simple query."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params=mysql_params)
        with connector as conn:
            results = connector.execute_query(conn, 'SELECT 1 AS test')
            assert results == [(1,)]
    except ConnectionError as e:
        pytest.skip(f'Could not connect to MySQL database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_connector_class_integration(postgres_params):
    """Test the database connector with actual credentials."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params=postgres_params)
        assert connector is not None
        assert connector.check_connection() is True
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS') or not os.environ.get('RUN_MYSQL_TESTS'),
    reason='MySQL database integration tests are disabled. Set both RUN_DB_TESTS=1 and RUN_MYSQL_TESTS=1 to enable.',
)
def test_mysql_connector_class_integration(mysql_params):
    """Test the MySQL database connector with actual credentials."""
    try:
        connector = DatabaseFactory.create_connector(DatabaseType.MYSQL, connection_params=mysql_params)
        assert connector is not None
        assert connector.check_connection() is True
    except ConnectionError as e:
        pytest.skip(f'Could not connect to MySQL database: {str(e)}')
