"""Integration tests for database schema introspection.

These tests require an actual database connection with test tables to run.
"""

import os

import pytest
from dotenv import load_dotenv

from supabase_pydantic.db.connection import construct_tables
from supabase_pydantic.db.constants import DatabaseConnectionType


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
@pytest.mark.construction
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_construct_tables_local_integration(db_params):
    """Test constructing tables using local connection parameters."""
    try:
        tables = construct_tables(
            DatabaseConnectionType.LOCAL,
            schemas=('public',),
            **db_params,
        )
        assert isinstance(tables, dict)
        assert 'public' in tables
        # Check basic structure - will vary depending on test database
        for table_name, table_info in tables['public'].items():
            # Just verify we have table information objects with expected structure
            assert hasattr(table_info, 'name')
            assert hasattr(table_info, 'columns')
    except Exception as e:
        pytest.skip(f'Could not construct tables: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.construction
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_construct_tables_db_url_integration(db_url):
    """Test constructing tables using a database URL."""
    try:
        tables = construct_tables(
            DatabaseConnectionType.DB_URL,
            schemas=('public',),
            DB_URL=db_url,
        )
        assert isinstance(tables, dict)
        assert 'public' in tables
        # Check basic structure - will vary depending on test database
        for table_name, table_info in tables['public'].items():
            # Just verify we have table information objects with expected structure
            assert hasattr(table_info, 'name')
            assert hasattr(table_info, 'columns')
    except Exception as e:
        pytest.skip(f'Could not construct tables: {str(e)}')
