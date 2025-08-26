"""Tests for PostgreSQL constraint marshaler implementation."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.marshalers.postgres.constraints import PostgresConstraintMarshaler


@pytest.fixture
def marshaler():
    """Fixture to create a PostgresConstraintMarshaler instance."""
    return PostgresConstraintMarshaler()


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_def, expected',
    [
        ('FOREIGN KEY (order_id) REFERENCES orders(id)', ('order_id', 'orders', 'id')),
        ('FOREIGN KEY (user_id) REFERENCES users(id)', ('user_id', 'users', 'id')),
        ('NOT A FOREIGN KEY', None),
    ],
)
def test_parse_foreign_key(marshaler, constraint_def, expected):
    """Test parsing foreign key constraint definition."""
    with patch('supabase_pydantic.db.marshalers.constraints.parse_constraint_definition_for_fk', return_value=expected):
        result = marshaler.parse_foreign_key(constraint_def)
        assert result == expected, f'Failed for {constraint_def}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_def, expected',
    [
        ('UNIQUE (email)', ['email']),
        ('UNIQUE (first_name, last_name)', ['first_name', 'last_name']),
        ('NOT A UNIQUE CONSTRAINT', []),
    ],
)
def test_parse_unique_constraint(marshaler, constraint_def, expected):
    """Test parsing unique constraint definition."""
    result = marshaler.parse_unique_constraint(constraint_def)
    assert result == expected, f'Failed for {constraint_def}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_def, expected',
    [
        ('CHECK (age > 0)', 'CHECK (age > 0)'),
        ('CHECK (price > 0 AND price < 1000)', 'CHECK (price > 0 AND price < 1000)'),
    ],
)
def test_parse_check_constraint(marshaler, constraint_def, expected):
    """Test parsing check constraint definition."""
    result = marshaler.parse_check_constraint(constraint_def)
    assert result == expected, f'Failed for {constraint_def}, got {result}, expected {expected}'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_constraints_to_table_details(marshaler):
    """Test adding constraints to table details."""
    # Mock data
    tables = {}
    constraint_data = []
    schema = 'public'

    # Use the correct import path with the alias as used in constraints.py
    with patch('supabase_pydantic.db.marshalers.postgres.constraints.add_constraints') as mock_add:
        # Call the method
        marshaler.add_constraints_to_table_details(tables, constraint_data, schema)

        # Verify the underlying function was called with correct arguments
        mock_add.assert_called_once_with(tables, schema, constraint_data)
