"""Tests for PostgresRelationshipMarshaler.analyze_table_relationships method."""

import pytest

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.postgres.relationship import PostgresRelationshipMarshaler
from supabase_pydantic.db.models import ColumnInfo, ForeignKeyInfo, TableInfo


@pytest.fixture
def marshaler():
    """Fixture to create a PostgresRelationshipMarshaler instance."""
    return PostgresRelationshipMarshaler()


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_analyze_table_relationships(marshaler):
    """Test that analyze_table_relationships correctly processes table relationships."""
    # Create mock tables with foreign keys
    tables = {
        ('public', 'users'): TableInfo(
            name='users',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', datatype='integer', is_unique=True, primary=True)
            ],
        ),
        ('public', 'orders'): TableInfo(
            name='orders',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', datatype='integer', is_unique=True, primary=True),
                ColumnInfo(
                    name='user_id', post_gres_datatype='integer', datatype='integer', is_unique=False, primary=False
                ),
            ],
        ),
    }

    # Add foreign key to orders table
    tables[('public', 'orders')].foreign_keys.append(
        ForeignKeyInfo(
            constraint_name='fk_user_id',
            column_name='user_id',
            foreign_table_name='users',
            foreign_column_name='id',
            foreign_table_schema='public',
        )
    )

    # Call the method
    marshaler.analyze_table_relationships(tables)

    # Verify relationships were analyzed
    assert tables[('public', 'orders')].foreign_keys[0].relation_type is not None

    # Since user_id is not unique in orders but id is unique in users,
    # this should be a MANY_TO_ONE relationship from orders to users
    assert tables[('public', 'orders')].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE
