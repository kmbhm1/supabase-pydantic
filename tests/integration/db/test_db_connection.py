"""Integration tests for database connection functionality.

These tests require an actual database connection to run.
"""

import os

import pytest
from dotenv import load_dotenv

from supabase_pydantic.db.connection import (
    DBConnection,
    check_connection,
    create_connection,
    create_connection_from_db_url,
    query_database,
)
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.exceptions import ConnectionError


# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def db_params():
    """Get database connection parameters from environment variables."""
    return {
        'DB_NAME': os.environ.get('TEST_DB_NAME', 'postgres'),
        'DB_USER': os.environ.get('TEST_DB_USER', 'postgres'),
        'DB_PASS': os.environ.get('TEST_DB_PASS', 'postgres'),
        'DB_HOST': os.environ.get('TEST_DB_HOST', 'localhost'),
        'DB_PORT': os.environ.get('TEST_DB_PORT', '5432'),
    }


@pytest.fixture
def db_url():
    """Get database URL from environment variables."""
    return os.environ.get(
        'TEST_DB_URL',
        'postgresql://postgres:postgres@localhost:5432/postgres',
    )


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_create_connection_integration(db_params):
    """Test creating a database connection with actual credentials."""
    try:
        conn = create_connection(
            db_params['DB_NAME'],
            db_params['DB_USER'],
            db_params['DB_PASS'],
            db_params['DB_HOST'],
            db_params['DB_PORT'],
        )
        assert conn is not None
        assert check_connection(conn) is True
        conn.close()
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_create_connection_from_db_url_integration(db_url):
    """Test creating a database connection from a URL with actual credentials."""
    try:
        conn = create_connection_from_db_url(db_url)
        assert conn is not None
        assert check_connection(conn) is True
        conn.close()
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_query_database_integration(db_params):
    """Test querying the database with a simple query."""
    try:
        conn = create_connection(
            db_params['DB_NAME'],
            db_params['DB_USER'],
            db_params['DB_PASS'],
            db_params['DB_HOST'],
            db_params['DB_PORT'],
        )
        results = query_database(conn, 'SELECT 1 AS test')
        assert results == [(1,)]
        conn.close()
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_db_connection_class_integration(db_params):
    """Test the DBConnection class with actual credentials."""
    try:
        db_connection = DBConnection(
            DatabaseConnectionType.LOCAL,
            **db_params,
        )
        assert db_connection.conn is not None
        assert check_connection(db_connection.conn) is True
        db_connection.conn.close()
    except ConnectionError as e:
        pytest.skip(f'Could not connect to database: {str(e)}')
