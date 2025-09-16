"""Tests for PostgreSQL schema marshaler implementation."""

import pytest
from unittest.mock import patch, MagicMock

from supabase_pydantic.db.marshalers.postgres.schema import PostgresSchemaMarshaler
from supabase_pydantic.db.models import TableInfo
from supabase_pydantic.db.database_type import DatabaseType


@pytest.fixture
def marshaler():
    """Fixture to create a PostgresSchemaMarshaler instance."""
    column_marshaler = MagicMock()
    constraint_marshaler = MagicMock()
    relationship_marshaler = MagicMock()

    return PostgresSchemaMarshaler(
        column_marshaler=column_marshaler,
        constraint_marshaler=constraint_marshaler,
        relationship_marshaler=relationship_marshaler,
    )


@pytest.fixture
def sample_column_data():
    """Sample column data for testing."""
    return [
        # Format: (table_schema, table_name, table_type, column_name, column_type, is_nullable,
        # column_default, is_unique, data_type, udt_schema, udt_name, primary)
        (
            'public',
            'users',
            'BASE TABLE',
            'id',
            'integer',
            'NO',
            "nextval('users_id_seq'::regclass)",
            True,
            'integer',
            'pg_catalog',
            'int4',
            True,
        ),
        (
            'public',
            'users',
            'BASE TABLE',
            'name',
            'character varying',
            'NO',
            None,
            False,
            'varchar',
            'pg_catalog',
            'varchar',
            False,
        ),
        (
            'public',
            'users',
            'BASE TABLE',
            'email',
            'character varying',
            'NO',
            None,
            True,
            'varchar',
            'pg_catalog',
            'varchar',
            False,
        ),
    ]


@pytest.fixture
def sample_fk_data():
    """Sample foreign key data for testing."""
    return [
        # Format: (table_schema, table_name, column_name, foreign_table_schema, foreign_table_name,
        # foreign_column_name, constraint_name)
        ('public', 'posts', 'user_id', 'public', 'users', 'id', 'fk_posts_user_id'),
        ('public', 'comments', 'post_id', 'public', 'posts', 'id', 'fk_comments_post_id'),
    ]


@pytest.fixture
def sample_constraint_data():
    """Sample constraint data for testing."""
    return [
        # Format: (schema_name, table_name, constraint_name, constraint_type, definition)
        ('public', 'users', 'pk_users', 'p', 'PRIMARY KEY (id)'),
        ('public', 'users', 'unique_email', 'u', 'UNIQUE (email)'),
        ('public', 'posts', 'check_title_length', 'c', 'CHECK (length(title) > 5)'),
    ]


@pytest.fixture
def sample_type_data():
    """Sample user-defined type data for testing."""
    return [
        # Format: (typname, typtype, typcategory)
        ('status_enum', 'e', 'E'),
        ('address_type', 'c', 'C'),
    ]


@pytest.fixture
def sample_type_mapping_data():
    """Sample type mapping data for testing."""
    return [
        # Format: (typname, enumlabel)
        ('status_enum', 'active'),
        ('status_enum', 'inactive'),
        ('status_enum', 'pending'),
    ]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_columns(marshaler, sample_column_data):
    """Test that column data is passed through unchanged."""
    result = marshaler.process_columns(sample_column_data)
    assert result == sample_column_data
    assert id(result) == id(sample_column_data), 'Result should be the same object instance'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_foreign_keys(marshaler, sample_fk_data):
    """Test that foreign key data is passed through unchanged."""
    result = marshaler.process_foreign_keys(sample_fk_data)
    assert result == sample_fk_data
    assert id(result) == id(sample_fk_data), 'Result should be the same object instance'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_constraints(marshaler, sample_constraint_data):
    """Test that constraint data is passed through unchanged."""
    result = marshaler.process_constraints(sample_constraint_data)
    assert result == sample_constraint_data
    assert id(result) == id(sample_constraint_data), 'Result should be the same object instance'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_table_details_from_columns(marshaler, sample_column_data):
    """Test getting table details from column data."""
    # Mock the column marshaler
    marshaler.column_marshaler = MagicMock()

    # Setup the mock to return a specific data type
    mock_processed_type = 'processed_integer'
    marshaler.column_marshaler.process_column_type.return_value = mock_processed_type

    # Call the method being tested
    with patch('supabase_pydantic.db.marshalers.postgres.schema.get_table_details_from_columns') as mock_get_details:
        mock_get_details.return_value = {
            ('public', 'users'): TableInfo(name='users', schema='public', table_type='BASE TABLE')
        }

        result = marshaler.get_table_details_from_columns(sample_column_data)

        # Check the result
        assert result == mock_get_details.return_value

        # Verify get_table_details_from_columns was called with the processed column data
        mock_get_details.assert_called_once_with(sample_column_data, False, column_marshaler=marshaler.column_marshaler)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_construct_table_info(
    marshaler, sample_column_data, sample_fk_data, sample_constraint_data, sample_type_data, sample_type_mapping_data
):
    """Test table info construction from database details."""
    # Mock the various methods called in construct_table_info
    with (
        patch('supabase_pydantic.db.marshalers.postgres.schema.get_table_details_from_columns') as mock_get_details,
        patch('supabase_pydantic.db.marshalers.postgres.schema.add_foreign_key_info_to_table_details') as mock_add_fk,
        patch(
            'supabase_pydantic.db.marshalers.postgres.schema.add_constraints_to_table_details'
        ) as mock_add_constraints,
        patch(
            'supabase_pydantic.db.marshalers.postgres.schema.add_relationships_to_table_details'
        ) as mock_add_relations,
        patch('supabase_pydantic.db.marshalers.postgres.schema.add_user_defined_types_to_tables') as mock_add_types,
        patch('supabase_pydantic.db.marshalers.postgres.schema.update_columns_with_constraints') as mock_update_cols,
        patch(
            'supabase_pydantic.db.marshalers.postgres.schema.update_column_constraint_definitions'
        ) as mock_update_constraints,
        patch('supabase_pydantic.db.marshalers.postgres.schema.analyze_bridge_tables') as mock_analyze_bridge,
        patch('supabase_pydantic.db.marshalers.postgres.schema.analyze_table_relationships') as mock_analyze_rel,
    ):
        # Setup the mock_get_details to return a dictionary with a sample table
        table_dict = {('public', 'users'): TableInfo(name='users', schema='public', table_type='BASE TABLE')}
        mock_get_details.return_value = table_dict

        # Mock the column marshaler
        marshaler.column_marshaler = MagicMock()

        # Call the method under test
        result = marshaler.construct_table_info(
            [],
            sample_column_data,
            sample_fk_data,
            sample_constraint_data,
            sample_type_data,
            sample_type_mapping_data,
            'public',
        )

        # Verify the result
        assert result == list(table_dict.values())

        # Verify all expected methods were called with correct parameters
        mock_get_details.assert_called_once()
        mock_add_fk.assert_called_once_with(table_dict, sample_fk_data)
        mock_add_constraints.assert_called_once_with(table_dict, 'public', sample_constraint_data)
        mock_add_relations.assert_called_once_with(table_dict, sample_fk_data)
        mock_add_types.assert_called_once_with(
            table_dict, 'public', sample_type_data, sample_type_mapping_data, DatabaseType.POSTGRES
        )
        mock_update_cols.assert_called_once_with(table_dict)
        mock_update_constraints.assert_called_once_with(table_dict)
        mock_analyze_bridge.assert_called_once_with(table_dict)

        # analyze_table_relationships should be called twice
        assert mock_analyze_rel.call_count == 2
        mock_analyze_rel.assert_called_with(table_dict)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_disable_model_prefix_protection(marshaler, sample_column_data):
    """Test that disable_model_prefix_protection is correctly passed through."""
    # Set the disable_model_prefix_protection attribute
    marshaler.disable_model_prefix_protection = True
    marshaler.column_marshaler = MagicMock()

    with patch('supabase_pydantic.db.marshalers.postgres.schema.get_table_details_from_columns') as mock_get_details:
        mock_get_details.return_value = {
            ('public', 'users'): TableInfo(name='users', schema='public', table_type='BASE TABLE')
        }

        marshaler.get_table_details_from_columns(sample_column_data)

        # Verify get_table_details_from_columns was called with the right flag value
        mock_get_details.assert_called_once_with(sample_column_data, True, column_marshaler=marshaler.column_marshaler)
