"""Tests for constraint marshaler functions in supabase_pydantic.db.marshalers.constraints."""

import pytest

from supabase_pydantic.db.models import (
    ColumnInfo,
    ConstraintInfo,
    TableInfo,
)
from supabase_pydantic.db.marshalers.constraints import (
    parse_constraint_definition_for_fk,
    update_column_constraint_definitions,
    update_columns_with_constraints,
)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_definition, expected',
    [
        ('FOREIGN KEY (user_id) REFERENCES users(id)', ('user_id', 'users', 'id')),
        ('FOREIGN KEY (order_id) REFERENCES orders(order_id)', ('order_id', 'orders', 'order_id')),
        ('INVALID KEY (order_id) REFERENCES orders(order_id)', None),  # Invalid format
        ('FOREIGN KEY (order_id) REF users(order_id)', None),  # Typo in SQL
        ('', None),  # Empty string
    ],
)
def test_parse_constraint_definition_for_fk(constraint_definition, expected):
    assert parse_constraint_definition_for_fk(constraint_definition) == expected, (
        f'Failed for definition: {constraint_definition}'
    )


@pytest.fixture
def tables_setup():
    # Create mock columns
    columns = [
        ColumnInfo(
            name='id', primary=False, is_unique=False, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'
        ),
        ColumnInfo(
            name='username',
            primary=False,
            is_unique=False,
            is_foreign_key=False,
            post_gres_datatype='text',
            datatype='str',
        ),
        ColumnInfo(
            name='order_id',
            primary=False,
            is_unique=False,
            is_foreign_key=False,
            post_gres_datatype='uuid',
            datatype='str',
        ),
    ]

    # Create mock constraints
    constraints = [
        ConstraintInfo(
            constraint_name='pk_users',
            columns=['id'],
            raw_constraint_type='p',
            constraint_definition='PRIMARY KEY (id)',
        ),
        ConstraintInfo(
            constraint_name='unique_username',
            columns=['username'],
            raw_constraint_type='u',
            constraint_definition='UNIQUE (username)',
        ),
        ConstraintInfo(
            constraint_name='fk_orders',
            columns=['order_id'],
            raw_constraint_type='f',
            constraint_definition='FOREIGN KEY (order_id) REFERENCES orders(order_id)',
        ),
    ]

    # Setup table info with these columns and constraints
    table = TableInfo(name='users', schema='public', table_type='BASE TABLE', columns=columns, constraints=constraints)

    # Dictionary with multiple tables
    tables = {
        ('public', 'users'): table,
        ('public', 'orders'): TableInfo(
            name='orders', schema='public', table_type='BASE TABLE', columns=[], constraints=constraints
        ),
        ('public', 'products'): TableInfo(
            name='products', schema='public', table_type='BASE TABLE', columns=columns, constraints=[]
        ),
    }
    return tables


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_update_columns_with_constraints(tables_setup):
    # Apply the update function
    tables_setup_copy = tables_setup.copy()
    update_columns_with_constraints(tables_setup_copy)

    # Get the updated table
    table = tables_setup_copy[('public', 'users')]

    # Assertions to check if columns were updated correctly
    assert table.columns[0].primary, 'ID should be marked as primary key'
    assert table.columns[1].is_unique, 'Username should be marked as unique'
    assert table.columns[2].is_foreign_key, 'Order ID should be marked as foreign key'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_update_column_constraint_definitions():
    """Test that update_column_constraint_definitions correctly updates columns with CHECK constraints."""
    # Create a test table with a column and constraint
    table = TableInfo(
        name='users',
        schema='public',
        table_type='BASE TABLE',
        columns=[
            ColumnInfo(
                name='age',
                primary=False,
                is_unique=False,
                is_foreign_key=False,
                post_gres_datatype='integer',
                datatype='int',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='age_check',
                columns=['age'],
                raw_constraint_type='c',
                constraint_definition='CHECK (age >= 0)',
            ),
        ],
    )

    # Create a dictionary of tables as expected by the function
    tables = {('public', 'users'): table}

    # Call the function
    update_column_constraint_definitions(tables)

    # Check that the column's constraint_definition field was updated
    assert table.columns[0].constraint_definition == 'CHECK (age >= 0)'

    # Test with multiple CHECK constraints on the same column
    table.constraints.append(
        ConstraintInfo(
            constraint_name='age_upper_check',
            columns=['age'],
            raw_constraint_type='c',
            constraint_definition='CHECK (age <= 120)',
        )
    )

    # Call the function again with the updated table
    tables = {('public', 'users'): table}
    update_column_constraint_definitions(tables)

    # The last constraint should be used
    assert table.columns[0].constraint_definition == 'CHECK (age <= 120)'
