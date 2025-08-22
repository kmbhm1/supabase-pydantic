"""Integration tests for seed data generation.

These tests require an actual database connection with test tables to run.
"""

import os

import pytest
from dotenv import load_dotenv

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factory import DatabaseFactory
from supabase_pydantic.db.models import PostgresConnectionParams
from supabase_pydantic.db.seed.generator import generate_seed_data


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
    """Get schema reader for the database."""
    try:
        reader = DatabaseFactory.create_schema_reader(
            DatabaseType.POSTGRES,
            connector=DatabaseFactory.create_connector(
                DatabaseType.POSTGRES,
                connection_params=postgres_params
            )
        )
        return reader
    except Exception as e:
        pytest.skip(f'Could not create schema reader: {str(e)}')


@pytest.fixture
def tables(schema_reader):
    """Get table information from the database using schema reader."""
    try:
        tables_dict = {}
        schemas = schema_reader.get_schemas()
        for schema in schemas:
            if schema == 'public':  # Only get 'public' schema
                table_models = schema_reader.get_tables(schema)
                tables_dict[schema] = {}
                for table in table_models:
                    table.columns = schema_reader.get_columns(schema, table.name)
                    table.constraints = schema_reader.get_constraints(schema, table.name)
                    tables_dict[schema][table.name] = table
        return tables_dict
    except Exception as e:
        pytest.skip(f'Could not get tables: {str(e)}')


@pytest.mark.integration
@pytest.mark.db
@pytest.mark.seed
@pytest.mark.skipif(
    not os.environ.get('RUN_DB_TESTS'),
    reason='Database integration tests are disabled. Set RUN_DB_TESTS=1 to enable.',
)
def test_generate_seed_data_integration(tables):
    """Test generating seed data from actual database schema."""
    if not tables or 'public' not in tables:
        pytest.skip('No tables available for testing')

    tables_list = list(tables['public'].values())
    if not tables_list:
        pytest.skip('No tables available in public schema for testing')

    # Generate seed data
    seed_data = generate_seed_data(tables_list)

    # Basic structure validation
    assert isinstance(seed_data, dict)

    # Each table should have data rows
    for table_name, data_rows in seed_data.items():
        # First row should be column names
        assert len(data_rows) > 0

        # At least one row of data (could be just headers if no rows)
        if len(data_rows) > 1:
            # Check that all data rows have same number of columns as headers
            header_count = len(data_rows[0])
            for row in data_rows[1:]:
                assert len(row) == header_count
