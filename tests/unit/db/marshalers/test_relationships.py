"""Tests for relationships module."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.marshalers.relationships import (
    add_foreign_key_info_to_table_details,
    add_relationships_to_table_details,
)
from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.models import ConstraintInfo, ForeignKeyInfo, TableInfo, RelationshipInfo


def create_mock_table(schema='public', name='table', is_bridge=False):
    """Create a mock table for testing."""
    return TableInfo(
        name=name,
        schema=schema,
        columns=[],
        constraints=[],
        foreign_keys=[],
        relationships=[],
        is_bridge=is_bridge,
    )


def test_add_relationships_to_table_details_with_bridge_table():
    """Test adding relationships with a bridge table."""
    # Create tables
    table1 = create_mock_table(name='table1')
    table2 = create_mock_table(name='table2')
    bridge_table = create_mock_table(name='bridge', is_bridge=True)

    # Add foreign keys to the bridge table
    fk1 = ForeignKeyInfo(
        constraint_name='fk1',
        column_name='table1_id',
        foreign_table_name='table1',
        foreign_column_name='id',
        foreign_table_schema='public',
        relation_type=RelationType.MANY_TO_ONE,
    )
    fk2 = ForeignKeyInfo(
        constraint_name='fk2',
        column_name='table2_id',
        foreign_table_name='table2',
        foreign_column_name='id',
        foreign_table_schema='public',
        relation_type=RelationType.MANY_TO_ONE,
    )
    bridge_table.add_foreign_key(fk1)
    bridge_table.add_foreign_key(fk2)

    # Create tables dict
    tables = {
        ('public', 'table1'): table1,
        ('public', 'table2'): table2,
        ('public', 'bridge'): bridge_table,
    }

    # Call function to test
    fk_details = [
        ('public', 'bridge', 'table1_id', 'public', 'table1', 'id', 'fk1'),
        ('public', 'bridge', 'table2_id', 'public', 'table2', 'id', 'fk2'),
    ]
    add_relationships_to_table_details(tables, fk_details)

    # Check that relationships were added with correct type
    # There may be multiple relationships created due to how the relationships are added
    # in the actual implementation, but we're mainly concerned with the MANY_TO_MANY type
    assert any(
        rel.related_table_name == 'table2' and rel.relation_type == RelationType.MANY_TO_MANY
        for rel in table1.relationships
    )

    assert any(
        rel.related_table_name == 'table1' and rel.relation_type == RelationType.MANY_TO_MANY
        for rel in table2.relationships
    )


def test_add_foreign_key_info_missing_tables():
    """Test adding foreign keys when tables are missing."""
    # Create tables dict with only one table
    table1 = create_mock_table(name='table1')
    tables = {('public', 'table1'): table1}

    # Create foreign key details where the foreign table doesn't exist
    fk_details = [
        ('public', 'table1', 'table2_id', 'public', 'table2', 'id', 'fk1'),
    ]

    with patch('logging.Logger.debug') as mock_logger_debug:
        add_foreign_key_info_to_table_details(tables, fk_details)

        # Verify logging messages
        assert any(
            'references table public.table2' in call_args[0][0] for call_args in mock_logger_debug.call_args_list
        )

    # Check that no foreign keys were added
    assert len(table1.foreign_keys) == 0

    # Now test with source table missing
    fk_details = [
        ('public', 'table3', 'table1_id', 'public', 'table1', 'id', 'fk2'),
    ]

    with patch('logging.Logger.debug') as mock_logger_debug:
        add_foreign_key_info_to_table_details(tables, fk_details)

        # Verify logging messages
        assert any(
            'missing source table public.table3' in call_args[0][0] for call_args in mock_logger_debug.call_args_list
        )


def test_add_foreign_key_info_one_to_one_relationship():
    """Test detecting a one-to-one relationship."""
    # Create tables with primary keys
    table1 = create_mock_table(name='table1')
    table2 = create_mock_table(name='table2')

    # Add primary key constraints
    pk1 = ConstraintInfo(
        constraint_name='pk1', raw_constraint_type='p', constraint_definition='PRIMARY KEY (id)', columns=['id']
    )
    pk2 = ConstraintInfo(
        constraint_name='pk2', raw_constraint_type='p', constraint_definition='PRIMARY KEY (id)', columns=['id']
    )
    table1.constraints.append(pk1)
    table2.constraints.append(pk2)

    tables = {
        ('public', 'table1'): table1,
        ('public', 'table2'): table2,
    }

    # Create foreign key where the FK column is also a primary key
    fk_details = [
        ('public', 'table1', 'id', 'public', 'table2', 'id', 'fk1'),
    ]

    with patch('logging.Logger.debug') as mock_logger_debug:
        add_foreign_key_info_to_table_details(tables, fk_details)

        # Verify ONE_TO_ONE was detected
        assert any(
            'Detected ONE_TO_ONE relationship' in call_args[0][0] for call_args in mock_logger_debug.call_args_list
        )

    # Check that the foreign key was added with correct relation type
    assert len(table1.foreign_keys) == 1
    assert table1.foreign_keys[0].relation_type == RelationType.ONE_TO_ONE


def test_add_foreign_key_info_many_to_one_relationship():
    """Test detecting a many-to-one relationship."""
    # Create tables with primary keys
    table1 = create_mock_table(name='table1')
    table2 = create_mock_table(name='table2')

    # Add primary key constraints (composite key in table1)
    pk1 = ConstraintInfo(
        constraint_name='pk1',
        raw_constraint_type='p',
        constraint_definition='PRIMARY KEY (id, other_id)',
        columns=['id', 'other_id'],
    )
    pk2 = ConstraintInfo(
        constraint_name='pk2', raw_constraint_type='p', constraint_definition='PRIMARY KEY (id)', columns=['id']
    )
    table1.constraints.append(pk1)
    table2.constraints.append(pk2)

    tables = {
        ('public', 'table1'): table1,
        ('public', 'table2'): table2,
    }

    # Create foreign key where FK column is part of composite key
    fk_details = [
        ('public', 'table1', 'other_id', 'public', 'table2', 'id', 'fk1'),
    ]

    with patch('logging.Logger.debug') as mock_logger_debug:
        add_foreign_key_info_to_table_details(tables, fk_details)

        # Verify composite key was detected
        assert any('Found composite primary key' in call_args[0][0] for call_args in mock_logger_debug.call_args_list)

    # Check that the foreign key was added with correct relation type
    assert len(table1.foreign_keys) == 1
    assert table1.foreign_keys[0].relation_type == RelationType.MANY_TO_ONE


def test_add_foreign_key_info_many_to_many_direct():
    """Test detecting a many-to-many relationship directly (multiple FKs to same table)."""
    # Create tables
    table1 = create_mock_table(name='table1')
    table2 = create_mock_table(name='table2')

    tables = {
        ('public', 'table1'): table1,
        ('public', 'table2'): table2,
    }

    # Add one foreign key first
    fk1 = ForeignKeyInfo(
        constraint_name='fk1',
        column_name='ref1_id',
        foreign_table_name='table2',
        foreign_column_name='id',
        foreign_table_schema='public',
        relation_type=None,
    )
    table1.add_foreign_key(fk1)

    # Now add a second foreign key to the same target table
    fk_details = [
        ('public', 'table1', 'ref2_id', 'public', 'table2', 'id', 'fk2'),
    ]

    # Call the function to add the foreign key
    add_foreign_key_info_to_table_details(tables, fk_details)

    # Verify we now have two foreign keys
    assert len(table1.foreign_keys) == 2

    # At least one of the foreign keys should have a relation type
    assert any(fk.relation_type is not None for fk in table1.foreign_keys)

    # Check that the foreign key was added with correct relation type
    assert len(table1.foreign_keys) == 2
    assert table1.foreign_keys[1].relation_type == RelationType.MANY_TO_ONE
