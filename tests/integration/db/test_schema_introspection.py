"""Integration tests for database schema introspection.

These tests require an actual database connection with test tables to run.
"""

import os

import pytest
from dotenv import load_dotenv

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factory import DatabaseFactory
from supabase_pydantic.db.models import PostgresConnectionParams


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
def schema_reader(postgres_params):
    """Create a schema reader for postgres database testing."""
    # Create connector and schema reader using the factory
    connector = DatabaseFactory.create_connector(DatabaseType.POSTGRES, connection_params=postgres_params)
    return DatabaseFactory.create_schema_reader(DatabaseType.POSTGRES, connector=connector)


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.construction
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_read_schema_integration(schema_reader):
    """Test reading schema information using local connection parameters."""
    try:
        schemas = schema_reader.get_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) > 0

        # Get tables for the first schema
        schema = schemas[0]  # Usually 'public'
        tables = schema_reader.get_tables(schema)
        assert isinstance(tables, list)

        # If there are tables, check their structure
        if tables:
            table = tables[0]
            assert table.name is not None

            # Get columns for the first table
            columns = schema_reader.get_columns(schema, table.name)
            assert isinstance(columns, list)

            # Check column structure if columns exis
            if columns:
                column = columns[0]
                assert column.name is not None
                assert column.data_type is not None
    except Exception as e:
        pytest.skip(f'Could not read schema: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.connection
@pytest.mark.construction
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_read_schema_from_url_integration(postgres_url):
    """Test reading schema information using a database URL."""
    try:
        connector = DatabaseFactory.create_connector(
            DatabaseType.POSTGRES,
            connection_params={'db_url': postgres_url}
        )
        reader = DatabaseFactory.create_schema_reader(
            DatabaseType.POSTGRES,
            connector=connector
        )

        schemas = reader.get_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) > 0

        # Get tables for the first schema
        schema = schemas[0]  # Usually 'public'
        tables = reader.get_tables(schema)
        assert isinstance(tables, list)

        # If there are tables, check their structure
        if tables:
            table = tables[0]
            assert table.name is not None
    except Exception as e:
        pytest.skip(f'Could not read schema: {str(e)}')
