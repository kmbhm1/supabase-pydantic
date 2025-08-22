"""Tests for MySQL constraint marshaler implementation."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.marshalers.mysql.constraints import MySQLConstraintMarshaler
from supabase_pydantic.db.models import TableInfo


@pytest.fixture
def marshaler():
    """Fixture to create a MySQLConstraintMarshaler instance."""
    return MySQLConstraintMarshaler()


@pytest.fixture
def tables_setup():
    """Create a fixture with tables for testing."""
    # Create mock table info
    users_table = TableInfo(name='users', schema='test_schema', table_type='BASE TABLE', columns=[], constraints=[])

    orders_table = TableInfo(name='orders', schema='test_schema', table_type='BASE TABLE', columns=[], constraints=[])

    # Dictionary with multiple tables
    tables = {
        ('test_schema', 'users'): users_table,
        ('test_schema', 'orders'): orders_table,
    }
    return tables


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_def, expected',
    [
        # Standard format
        ('FOREIGN KEY (user_id) REFERENCES users(id)', ('user_id', 'users', 'id')),
        # MySQL-specific format with backticks
        ('FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)', ('user_id', 'users', 'id')),
        # Mixed format (with and without backticks)
        ('FOREIGN KEY (`order_id`) REFERENCES orders (`order_id`)', ('order_id', 'orders', 'order_id')),
        # Invalid formats
        ('INVALID KEY (user_id) REFERENCES users(id)', None),
        ('FOREIGN REF `users` (`id`)', None),
        ('', None),
    ],
)
def test_parse_foreign_key(marshaler, constraint_def, expected):
    """Test MySQL foreign key parsing."""
    result = marshaler.parse_foreign_key(constraint_def)
    assert result == expected, f"Failed for '{constraint_def}', got {result}, expected {expected}"


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_def, expected',
    [
        # Standard format
        ('UNIQUE (email)', ['email']),
        # Multiple columns
        ('UNIQUE (`email`, `username`)', ['email', 'username']),
        # With KEY keyword
        ('UNIQUE KEY `uk_email` (`email`)', ['email']),
        # Invalid formats
        ('UNIQ (`email`)', []),
        ('', []),
    ],
)
def test_parse_unique_constraint(marshaler, constraint_def, expected):
    """Test MySQL unique constraint parsing."""
    result = marshaler.parse_unique_constraint(constraint_def)
    assert result == expected, f"Failed for '{constraint_def}', got {result}, expected {expected}"


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@pytest.mark.parametrize(
    'constraint_def, expected',
    [
        ('CHECK (`age` > 0)', '`age` > 0'),
        ('CHECK (price > 0 AND price < 1000)', 'price > 0 AND price < 1000'),
        ("CHECK (`status` IN ('active', 'inactive'))", "`status` IN ('active', 'inactive')"),
        ('INVALID CHECK', 'INVALID CHECK'),  # Should return original if no match
    ],
)
def test_parse_check_constraint(marshaler, constraint_def, expected):
    """Test MySQL check constraint parsing."""
    result = marshaler.parse_check_constraint(constraint_def)
    assert result == expected, f"Failed for '{constraint_def}', got {result}, expected {expected}"


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_constraints_to_table_details(marshaler, tables_setup):
    """Test adding constraints to table details."""
    # Create mock constraint data
    constraint_data = [
        {'table_name': 'users', 'constraint_name': 'pk_users', 'constraint_type': 'PRIMARY KEY'},
        {'table_name': 'users', 'constraint_name': 'uk_email', 'constraint_type': 'UNIQUE'},
    ]

    # We'll patch the common implementation since that's what's used
    with patch('supabase_pydantic.db.marshalers.mysql.constraints.add_constraints') as mock_add_constraints:
        marshaler.add_constraints_to_table_details(tables_setup, constraint_data, 'test_schema')

        # Verify the common implementation was called with correct parameters
        mock_add_constraints.assert_called_once_with(tables_setup, 'test_schema', constraint_data)
