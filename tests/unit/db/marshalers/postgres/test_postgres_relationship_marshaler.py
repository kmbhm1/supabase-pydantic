"""Tests for PostgreSQL relationship marshaler implementation."""

import pytest

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.postgres.relationship import PostgresRelationshipMarshaler
from supabase_pydantic.db.models import ColumnInfo, TableInfo


@pytest.fixture
def marshaler():
    """Fixture to create a PostgresRelationshipMarshaler instance."""
    return PostgresRelationshipMarshaler()


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_initialize():
    """Test the initialization of PostgresRelationshipMarshaler."""
    marshaler = PostgresRelationshipMarshaler()
    assert isinstance(marshaler, PostgresRelationshipMarshaler)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'table_name, column_name, ref_table_name, ref_column_name, expected',
    [
        ('users', 'id', 'orders', 'user_id', RelationType.ONE_TO_MANY),
        ('orders', 'user_id', 'users', 'id', RelationType.MANY_TO_ONE),
        ('users', 'id', 'user_details', 'user_id', RelationType.ONE_TO_ONE),
        ('products', 'id', 'product_tags', 'product_id', RelationType.ONE_TO_MANY),
    ],
)
def test_determine_relationship_type(marshaler, table_name, column_name, ref_table_name, ref_column_name, expected):
    """Test determining relationship type between tables."""
    # Create TableInfo objects with appropriate column properties
    source_table = TableInfo(name=table_name, columns=[])
    target_table = TableInfo(name=ref_table_name, columns=[])

    # Add columns with appropriate uniqueness/primary flags based on the test case
    if expected == RelationType.ONE_TO_ONE:
        # Both sides are unique
        source_table.columns.append(
            ColumnInfo(
                name=column_name, post_gres_datatype='integer', datatype='integer', is_unique=True, primary=False
            )
        )
        target_table.columns.append(
            ColumnInfo(
                name=ref_column_name, post_gres_datatype='integer', datatype='integer', is_unique=True, primary=False
            )
        )
    elif expected == RelationType.ONE_TO_MANY:
        # Source is unique, target is not
        source_table.columns.append(
            ColumnInfo(
                name=column_name, post_gres_datatype='integer', datatype='integer', is_unique=True, primary=False
            )
        )
        target_table.columns.append(
            ColumnInfo(
                name=ref_column_name, post_gres_datatype='integer', datatype='integer', is_unique=False, primary=False
            )
        )
    elif expected == RelationType.MANY_TO_ONE:
        # Source is not unique, target is
        source_table.columns.append(
            ColumnInfo(
                name=column_name, post_gres_datatype='integer', datatype='integer', is_unique=False, primary=False
            )
        )
        target_table.columns.append(
            ColumnInfo(
                name=ref_column_name, post_gres_datatype='integer', datatype='integer', is_unique=True, primary=False
            )
        )
    else:
        # Neither is unique
        source_table.columns.append(
            ColumnInfo(
                name=column_name, post_gres_datatype='integer', datatype='integer', is_unique=False, primary=False
            )
        )
        target_table.columns.append(
            ColumnInfo(
                name=ref_column_name, post_gres_datatype='integer', datatype='integer', is_unique=False, primary=False
            )
        )

    result = marshaler.determine_relationship_type(source_table, target_table, column_name, ref_column_name)
    assert result == expected, (
        f'Failed for {table_name}.{column_name} -> {ref_table_name}.{ref_column_name}, '
        f'got {result}, expected {expected}'
    )


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_type_none_handling(marshaler):
    """Test handling of None values in determine_relationship_type."""
    # Create TableInfo objects with no column data
    source_table = TableInfo(name='table1', columns=[])
    target_table = TableInfo(name='table2', columns=[])

    # When columns don't exist, should default to MANY_TO_MANY
    result = marshaler.determine_relationship_type(source_table, target_table, 'col1', 'col2')
    assert result == RelationType.MANY_TO_MANY
