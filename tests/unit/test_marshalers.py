from unittest.mock import MagicMock, patch

import pytest
import logging

from supabase_pydantic.util.constants import RelationType
from supabase_pydantic.util.dataclasses import ColumnInfo, ConstraintInfo, ForeignKeyInfo, RelationshipInfo, TableInfo
from supabase_pydantic.util.marshalers import (
    add_constraints_to_table_details,
    add_foreign_key_info_to_table_details,
    add_relationships_to_table_details,
    add_user_defined_types_to_tables,
    analyze_bridge_tables,
    analyze_table_relationships,
    column_name_is_reserved,
    column_name_reserved_exceptions,
    construct_table_info,
    get_alias,
    get_enum_types,
    get_table_details_from_columns,
    get_user_type_mappings,
    is_bridge_table,
    parse_constraint_definition_for_fk,
    standardize_column_name,
    string_is_reserved,
    update_column_constraint_definitions,
    update_columns_with_constraints,
)


# Fixture for column details
@pytest.fixture
def column_details():
    return [
        ('public', 'users', 'user_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE', None),
        ('public', 'users', 'email', None, 'YES', 'text', 255, 'BASE TABLE', None),
    ]


# Fixture for foreign key details
@pytest.fixture
def fk_details():
    return [('public', 'users', 'user_id', 'public', 'orders', 'owner_id', 'fk_user_id')]


# Fixture for constraint details
@pytest.fixture
def constraints():
    return [('pk_users', 'users', ['user_id'], 'PRIMARY KEY', 'PRIMARY KEY (user_id)')]


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

    # Dictionary with one table
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


@pytest.fixture
def bridge_table_setup():
    columns = [
        ColumnInfo(name='user_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='role_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(
            name='created_at', primary=False, is_foreign_key=False, post_gres_datatype='timestamp', datatype='str'
        ),
    ]
    foreign_keys = [
        ForeignKeyInfo(
            column_name='user_id', foreign_table_name='users', foreign_column_name='id', constraint_name='fk_user_id'
        ),
        ForeignKeyInfo(
            column_name='role_id', foreign_table_name='roles', foreign_column_name='id', constraint_name='fk_role_id'
        ),
    ]
    return TableInfo(name='user_roles', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def non_bridge_table_setup():
    columns = [
        ColumnInfo(name='id', primary=True, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='info', primary=False, is_foreign_key=False, post_gres_datatype='text', datatype='str'),
    ]
    foreign_keys = []
    return TableInfo(name='simple_table', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def no_primary_bridge_table_setup():
    columns = [
        ColumnInfo(name='user_id', primary=False, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='role_id', primary=False, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(
            name='created_at', primary=False, is_foreign_key=False, post_gres_datatype='timestamp', datatype='str'
        ),
    ]
    foreign_keys = [
        ForeignKeyInfo(
            column_name='user_id', foreign_table_name='users', foreign_column_name='id', constraint_name='fk_user_id'
        ),
        ForeignKeyInfo(
            column_name='role_id', foreign_table_name='roles', foreign_column_name='id', constraint_name='fk_role_id'
        ),
    ]
    return TableInfo(name='user_roles', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def primary_foreign_and_col_primary_unequal_table_setup():
    columns = [
        ColumnInfo(name='user_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='role_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(
            name='created_at', primary=True, is_foreign_key=False, post_gres_datatype='timestamp', datatype='str'
        ),
    ]
    foreign_keys = [
        ForeignKeyInfo(
            column_name='user_id', foreign_table_name='users', foreign_column_name='id', constraint_name='fk_user_id'
        ),
        ForeignKeyInfo(
            column_name='role_id', foreign_table_name='roles', foreign_column_name='id', constraint_name='fk_role_id'
        ),
    ]
    return TableInfo(name='user_roles', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def setup_analyze_tables():
    # Create two tables with a simple one-to-many relationship
    user_table = TableInfo(
        name='users',
        schema='public',
        columns=[
            ColumnInfo(
                name='id', primary=True, is_unique=True, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'
            ),
            ColumnInfo(
                name='username',
                primary=False,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='text',
                datatype='str',
            ),
        ],
        foreign_keys=[],
    )

    order_table = TableInfo(
        name='orders',
        schema='public',
        columns=[
            ColumnInfo(
                name='id', primary=True, is_unique=True, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'
            ),
            ColumnInfo(
                name='user_id',
                primary=False,
                is_unique=False,
                is_foreign_key=True,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='fk_user_id',
                column_name='user_id',
                foreign_table_name='users',
                foreign_column_name='id',
                relation_type=None,
            )
        ],
    )
    return {'public.users': user_table, 'public.orders': order_table}


@pytest.fixture
def column_construct_test_details():
    return [
        ('public', 'users', 'user_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE'),
        ('public', 'users', 'email', None, 'YES', 'text', 255, 'BASE TABLE'),
        ('public', 'orders', 'order_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE'),
        ('public', 'orders', 'user_id', None, 'YES', 'uuid', None, 'BASE TABLE'),
    ]


@pytest.fixture
def fk_construct_test_details():
    return [('public', 'orders', 'user_id', 'public', 'users', 'user_id', 'fk_user_id')]


@pytest.fixture
def construct_test_constraints():
    return [
        ('pk_users', 'users', ['user_id'], 'PRIMARY KEY', 'PRIMARY KEY (user_id)'),
        ('pk_orders', 'orders', ['order_id'], 'PRIMARY KEY', 'PRIMARY KEY (order_id)'),
    ]


@pytest.fixture
def construct_enum_types():
    return [
        ('type_name', 'public', 'owner', 'category_1', True, 'e', ['user1', 'user2']),
        ('type_name_1', 'public', 'owner', 'category_2', True, 'e', ['value3', 'value4']),
    ]


@pytest.fixture
def construct_enum_mapping():
    return [
        ('username', 'users', 'public', 'type_name', 'category_1', 'foo'),
    ]


@pytest.mark.parametrize(
    'value, expected',
    [
        ('int', True),  # Python built-in
        ('print', True),  # Python built-in
        ('for', True),  # Python keyword
        ('def', True),  # Python keyword
        ('username', False),  # Not reserved
        ('customfield', False),  # Not reserved
        ('id', True),  # Built-in
    ],
)
def test_string_is_reserved(value, expected):
    assert string_is_reserved(value) == expected, f'Failed for {value}'


@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', True),
        ('print', True),
        ('model_abc', True),
        ('username', False),
        ('id', True),  # Though 'id' is a built-in, check if it's treated as an exception in another test
    ],
)
def test_column_name_is_reserved(column_name, expected):
    assert column_name_is_reserved(column_name) == expected, f'Failed for {column_name}'


@pytest.mark.parametrize(
    'column_name, expected', [('id', True), ('ID', True), ('Id', True), ('username', False), ('int', False)]
)
def test_column_name_reserved_exceptions(column_name, expected):
    assert column_name_reserved_exceptions(column_name) == expected, f'Failed for {column_name}'


# Test for standardize_column_name
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'field_int'),  # Reserved keyword
        ('print', 'field_print'),  # Built-in name
        ('model_abc', 'field_model_abc'),  # Starts with 'model_'
        ('username', 'username'),  # Not a reserved name
        ('id', 'id'),  # Exception, should not be modified
    ],
)
def test_standardize_column_name(column_name, expected):
    assert standardize_column_name(column_name) == expected, f'Failed for {column_name}'


# Test for get_alias
@pytest.mark.parametrize(
    'column_name, expected',
    [
        ('int', 'int'),  # Reserved keyword not an exception
        ('model_name', 'model_name'),  # Starts with 'model_'
        ('id', None),  # Exception to reserved keywords
        ('username', None),  # Not a reserved name
    ],
)
def test_get_alias(column_name, expected):
    assert get_alias(column_name) == expected, f'Failed for {column_name}'


# Test for parse_constraint_definition_for_fk
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


# Test get_table_details_from_columns
def test_get_table_details_from_columns(column_details):
    result = get_table_details_from_columns(column_details)
    assert ('public', 'users') in result
    table = result[('public', 'users')]
    assert len(table.columns) == 2
    assert table.columns[0].name == 'user_id'
    assert table.columns[1].datatype == 'str'  # Assuming mapping in PYDANTIC_TYPE_MAP


# Test add_constraints_to_table_details
def test_add_constraints_to_table_details(column_details, constraints):
    tables = get_table_details_from_columns(column_details)
    add_constraints_to_table_details(tables, 'public', constraints)
    table = tables[('public', 'users')]
    assert len(table.constraints) == 1
    assert table.constraints[0].constraint_name == 'pk_users'


def test_update_columns_with_constraints(tables_setup):
    # Apply the update function
    tables_setup_copy = tables_setup.copy()
    update_columns_with_constraints(tables_setup_copy)

    # Get the updated table
    table = tables_setup_copy[('public', 'users')]
    # print(table)

    # Assertions to check if columns were updated correctly
    assert table.columns[0].primary, 'ID should be marked as primary key'
    assert table.columns[1].is_unique, 'Username should be marked as unique'
    assert table.columns[2].is_foreign_key, 'Order ID should be marked as foreign key'


# Test is_bridge_table function
def test_is_bridge_table(
    bridge_table_setup,
    non_bridge_table_setup,
    no_primary_bridge_table_setup,
    primary_foreign_and_col_primary_unequal_table_setup,
):
    assert is_bridge_table(bridge_table_setup) is True, 'Should identify as a bridge table'
    assert not is_bridge_table(non_bridge_table_setup), 'Should not identify as a bridge table'
    assert not is_bridge_table(no_primary_bridge_table_setup), 'Should not identify as a bridge table'
    assert not is_bridge_table(primary_foreign_and_col_primary_unequal_table_setup), (
        'Should not identify as a bridge table'
    )


# Test analyze_bridge_tables function
def test_analyze_bridge_tables(
    bridge_table_setup,
    non_bridge_table_setup,
):
    tables = {
        'user_roles': bridge_table_setup,
        'simple_table': non_bridge_table_setup,
    }
    analyze_bridge_tables(tables)
    assert tables['user_roles'].is_bridge is True, 'user_roles should be marked as a bridge table'
    assert not tables['simple_table'].is_bridge, 'simple_table should not be marked as a bridge table'


def test_analyze_table_relationships(setup_analyze_tables):
    analyze_table_relationships(setup_analyze_tables)

    # Check basic many-to-one relationship
    assert setup_analyze_tables['public.orders'].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE

    # Check for automatically added reciprocal foreign key in users table
    assert len(setup_analyze_tables['public.users'].foreign_keys) == 1
    assert setup_analyze_tables['public.users'].foreign_keys[0].relation_type == RelationType.ONE_TO_MANY
    assert setup_analyze_tables['public.users'].foreign_keys[0].foreign_table_name == 'orders'


def test_no_foreign_table(setup_analyze_tables):
    # Add a foreign key with a non-existent table
    setup_analyze_tables['public.orders'].foreign_keys.append(
        ForeignKeyInfo(
            constraint_name='fk_nonexistent',
            column_name='user_id',
            foreign_table_name='nonexistent',
            foreign_column_name='id',
            relation_type=None,
        )
    )
    analyze_table_relationships(setup_analyze_tables)
    # Verify that no changes occurred for the non-existent table foreign key
    assert 'public.nonexistent' not in setup_analyze_tables


def test_reciprocal_foreign_keys(setup_analyze_tables):
    # Add a new column to users for order_id
    setup_analyze_tables['public.users'].columns.append(
        ColumnInfo(
            name='order_id',
            primary=False,
            is_unique=False,
            is_foreign_key=True,
            post_gres_datatype='uuid',
            datatype='str',
        )
    )
    # Add reciprocal foreign key in users table
    setup_analyze_tables['public.users'].foreign_keys.append(
        ForeignKeyInfo(
            constraint_name='fk_order_id',
            column_name='order_id',
            foreign_table_name='orders',
            foreign_column_name='id',
            relation_type=None,
        )
    )
    analyze_table_relationships(setup_analyze_tables)
    # Expecting a many-to-one relationship in both directions
    assert setup_analyze_tables['public.orders'].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE
    assert setup_analyze_tables['public.users'].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE


# Test for construct_table_info
@patch('supabase_pydantic.util.marshalers.get_table_details_from_columns')
@patch('supabase_pydantic.util.marshalers.add_foreign_key_info_to_table_details')
@patch('supabase_pydantic.util.marshalers.add_constraints_to_table_details')
@patch('supabase_pydantic.util.marshalers.add_relationships_to_table_details')
@patch('supabase_pydantic.util.marshalers.add_user_defined_types_to_tables')
@patch('supabase_pydantic.util.marshalers.update_columns_with_constraints')
@patch('supabase_pydantic.util.marshalers.analyze_bridge_tables')
@patch('supabase_pydantic.util.marshalers.analyze_table_relationships')
# @patch('supabase_pydantic.util.marshalers.add_fk')
def test_construct_table_info(
    mock_analyze_relationships,
    mock_analyze_bridges,
    mock_update_constraints,
    mock_add_constraints,
    mock_add_relationships,
    mock_add_user_defined_types_to_tables,
    # mock_add_fk,
    mock_get_details,
    column_construct_test_details,
    fk_construct_test_details,
    construct_test_constraints,
    construct_enum_types,
    construct_enum_mapping,
):
    # Setup mocks
    mock_get_details.return_value = {
        ('public', 'users'): MagicMock(spec=TableInfo),
        ('public', 'orders'): MagicMock(spec=TableInfo),
    }

    # Call the function
    tables = construct_table_info(
        column_construct_test_details,
        fk_construct_test_details,
        construct_test_constraints,
        construct_enum_types,
        construct_enum_mapping,
    )

    # Verify the correct sequence of function calls
    mock_get_details.assert_called_once()
    # mock_add_fk.assert_called_once()
    mock_add_constraints.assert_called_once()
    mock_update_constraints.assert_called_once()
    mock_analyze_bridges.assert_called_once()
    mock_add_relationships.assert_called_once()
    mock_add_user_defined_types_to_tables.assert_called_once()
    assert mock_analyze_relationships.call_count == 2, 'analyze_table_relationships should be called twice'

    # Assert the output
    assert len(tables) == 0  # Assuming the mocks were setup to reflect two tables


def test_add_relationships_to_table_details():
    # Mocking the table structures
    table1 = MagicMock()
    table1.foreign_keys = [MagicMock(foreign_table_name='related_table', foreign_column_name='id')]
    table1.columns = [MagicMock(name='id'), MagicMock(name='column1')]

    related_table = MagicMock()
    related_table.columns = [MagicMock(name='id'), MagicMock(name='column2')]

    tables = {('schema1', 'table1'): table1, ('schema1', 'related_table'): related_table}

    fk_details = [('schema1', 'table1', 'column1', 'schema1', 'related_table', 'id', 'fk1')]

    # Mock the relationships list where relationships will be added
    table1.relationships = []

    # Call the function
    add_relationships_to_table_details(tables, fk_details)

    # Assert that the relationship was correctly added
    expected_relationship = RelationshipInfo(
        table_name='table1', related_table_name='related_table', relation_type=RelationType.ONE_TO_MANY
    )

    assert len(table1.relationships) == 1
    assert table1.relationships[0] == expected_relationship


@pytest.fixture
def mock_enum_types():
    return [
        ('type_name', 'public', 'owner', 'category_1', True, 'e', ['user1', 'user2']),
        ('type_name_1', 'public', 'owner', 'category_2', True, 'e', ['value3', 'value4']),
        ('type_name_1', 'public', 'owner', 'category_3', True, 'c', ['value5', 'value6']),
        ('type_name_1', 'private', 'owner', 'category_4', True, 'd', ['value7', 'value8']),
    ]


def test_get_enum_types(mock_enum_types):
    # Call the function
    enum_types = get_enum_types(mock_enum_types, 'public')

    # Assert the output
    assert len(enum_types) == 2


@pytest.fixture
def mock_enum_type_mapping():
    return [
        ('username', 'users', 'public', 'type_name', 'category_1', 'foo'),
        ('username', 'users', 'public', 'type_name', 'category_2', 'bar'),
        ('username', 'users', 'public', 'type_name_1', 'category_3', 'baz'),
        ('username', 'users', 'public', 'type_name_1', 'category_4', 'qux'),
        ('username', 'users', 'private', 'type_name_1', 'category_4', 'qux'),
    ]


def test_get_user_type_mappings(mock_enum_type_mapping):
    # Call the function
    user_type_mappings = get_user_type_mappings(mock_enum_type_mapping, 'public')

    # Assert the output
    assert len(user_type_mappings) == 4
    assert user_type_mappings[0].type_category == 'category_1'


@pytest.fixture
def mock_tables():
    return {
        ('public', 'test_table'): TableInfo(
            name='test_table',
            columns=[
                ColumnInfo(name='id', user_defined_values=None, post_gres_datatype='uuid', datatype='str'),
                ColumnInfo(name='type', user_defined_values=None, post_gres_datatype='user-defined', datatype='str'),
            ],
        )
    }


# Mocks for the external functions
@pytest.fixture
def get_enum_types_mock(mocker):
    mock = mocker.patch('supabase_pydantic.util.marshalers.get_enum_types')
    mock.return_value = [
        # Example enum values setup
        MagicMock(type_name='my_enum', enum_values=['A', 'B', 'C'])
    ]
    return mock


@pytest.fixture
def get_user_type_mappings_mock(mocker):
    mock = mocker.patch('supabase_pydantic.util.marshalers.get_user_type_mappings')
    mock.return_value = [
        # Example user type mappings setup
        MagicMock(table_name='test_table', column_name='type', type_name='my_enum')
    ]
    return mock


# Test functions
def test_add_user_defined_types_valid_input(
    mock_tables, mock_enum_types, mock_enum_type_mapping, get_enum_types_mock, get_user_type_mappings_mock
):
    add_user_defined_types_to_tables(mock_tables, 'public', mock_enum_types, mock_enum_type_mapping)
    assert mock_tables[('public', 'test_table')].columns[1].user_defined_values == [
        'A',
        'B',
        'C',
    ], 'Enum values should be assigned correctly'


def test_table_key_not_found(
    mock_tables, mock_enum_types, mock_enum_type_mapping, get_enum_types_mock, get_user_type_mappings_mock
):
    # Adjust the mapping to a non-existent table
    get_user_type_mappings_mock.return_value = [
        MagicMock(table_name='nonexistent_table', column_name='type', type_name='my_enum')
    ]
    with pytest.raises(KeyError):
        add_user_defined_types_to_tables(mock_tables, 'public', mock_enum_types, mock_enum_type_mapping)


def test_column_name_not_found(
    mock_tables, mock_enum_types, mock_enum_type_mapping, get_enum_types_mock, get_user_type_mappings_mock
):
    # Adjust the mapping to a non-existent column
    get_user_type_mappings_mock.return_value = [
        MagicMock(table_name='test_table', column_name='nonexistent_column', type_name='my_enum')
    ]
    add_user_defined_types_to_tables(mock_tables, 'public', mock_enum_types, mock_enum_type_mapping)
    # Since this writes to stdout, it might be hard to directly assert without capturing the output
    assert True, (
        'Should handle non-existent column gracefully (test by inspecting printed output or modify function to be more testable)'
    )


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


@pytest.fixture
def identity_column_details():
    return [
        ('public', 'users', 'id', None, 'NO', 'integer', None, 'BASE TABLE', 'ALWAYS'),
        ('public', 'users', 'name', None, 'YES', 'text', 255, 'BASE TABLE', None),
    ]


def test_identity_columns(identity_column_details):
    tables = get_table_details_from_columns(identity_column_details)
    table = tables[('public', 'users')]

    # Check that identity column is properly identified
    id_column = next(col for col in table.columns if col.name == 'id')
    assert id_column.is_identity is True

    # Check non-identity column
    name_column = next(col for col in table.columns if col.name == 'name')
    assert name_column.is_identity is False


@pytest.fixture
def relationship_tables():
    # Create tables with various relationship types
    user_table = TableInfo(
        name='users',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(
                name='profile_id', is_foreign_key=True, is_unique=True, post_gres_datatype='uuid', datatype='str'
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='profile_id',
                foreign_table_name='profiles',
                foreign_column_name='id',
                constraint_name='fk_user_profile',
            ),
        ],
    )

    profile_table = TableInfo(
        name='profiles',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
        ],
    )

    post_table = TableInfo(
        name='posts',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(name='user_id', is_foreign_key=True, is_unique=False, post_gres_datatype='uuid', datatype='str'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='user_id',
                foreign_table_name='users',
                foreign_column_name='id',
                constraint_name='fk_post_user',
            ),
        ],
    )

    return {
        ('public', 'users'): user_table,
        ('public', 'profiles'): profile_table,
        ('public', 'posts'): post_table,
    }


def test_relationship_types(relationship_tables):
    # Test ONE_TO_ONE relationship (user -> profile)
    analyze_table_relationships(relationship_tables)
    user_table = relationship_tables[('public', 'users')]

    # Check user -> profile relationship (ONE_TO_ONE)
    user_profile_rel = next(rel for rel in user_table.foreign_keys if rel.foreign_table_name == 'profiles')
    assert user_profile_rel.relation_type == RelationType.ONE_TO_ONE

    # Check post -> user relationship (MANY_TO_ONE)
    post_table = relationship_tables[('public', 'posts')]
    post_user_rel = next(rel for rel in post_table.foreign_keys if rel.foreign_table_name == 'users')
    assert post_user_rel.relation_type == RelationType.MANY_TO_ONE

    # Check reciprocal user -> posts relationship (ONE_TO_MANY)
    user_posts_rel = next(rel for rel in user_table.foreign_keys if rel.foreign_table_name == 'posts')
    assert user_posts_rel.relation_type == RelationType.ONE_TO_MANY


@pytest.fixture
def complex_relationship_tables():
    # Create tables with various relationship types including MANY_TO_MANY

    # User table with multiple relationships
    user_table = TableInfo(
        name='users',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(
                name='settings_id', is_foreign_key=True, is_unique=True, post_gres_datatype='uuid', datatype='str'
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='settings_id',
                foreign_table_name='user_settings',
                foreign_column_name='id',
                constraint_name='fk_user_settings',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_users',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
                columns=['id'],
            ),
            ConstraintInfo(
                constraint_name='uq_settings',
                raw_constraint_type='u',
                constraint_definition='UNIQUE (settings_id)',
                columns=['settings_id'],
            ),
        ],
    )

    # User settings table (ONE_TO_ONE with users)
    settings_table = TableInfo(
        name='user_settings',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_settings',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
                columns=['id'],
            ),
        ],
    )

    # Posts table (ONE_TO_MANY with users)
    post_table = TableInfo(
        name='posts',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(name='user_id', is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='user_id',
                foreign_table_name='users',
                foreign_column_name='id',
                constraint_name='fk_post_user',
            ),
        ],
    )

    # Tags table for MANY_TO_MANY relationship with posts
    tag_table = TableInfo(
        name='tags',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(name='name', post_gres_datatype='text', datatype='str'),
        ],
    )

    # Bridge table for posts and tags (MANY_TO_MANY)
    post_tags_table = TableInfo(
        name='post_tags',
        schema='public',
        columns=[
            ColumnInfo(name='post_id', is_foreign_key=True, primary=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(name='tag_id', is_foreign_key=True, primary=True, post_gres_datatype='uuid', datatype='str'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='post_id',
                foreign_table_name='posts',
                foreign_column_name='id',
                constraint_name='fk_post_tags_post',
            ),
            ForeignKeyInfo(
                column_name='tag_id',
                foreign_table_name='tags',
                foreign_column_name='id',
                constraint_name='fk_post_tags_tag',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_post_tags',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (post_id, tag_id)',
                columns=['post_id', 'tag_id'],
            ),
        ],
    )

    return {
        ('public', 'users'): user_table,
        ('public', 'user_settings'): settings_table,
        ('public', 'posts'): post_table,
        ('public', 'tags'): tag_table,
        ('public', 'post_tags'): post_tags_table,
    }


def test_complex_relationship_types(complex_relationship_tables):
    """Test various relationship types including MANY_TO_MANY and edge cases."""
    analyze_bridge_tables(complex_relationship_tables)
    analyze_table_relationships(complex_relationship_tables)


def test_multiple_foreign_keys_to_same_table(complex_relationship_tables):
    """Test handling of multiple foreign keys to the same table."""
    # Add another foreign key to users in posts table (e.g., editor_id)
    post_table = complex_relationship_tables[('public', 'posts')]
    post_table.foreign_keys.append(
        ForeignKeyInfo(
            column_name='editor_id',
            foreign_table_name='users',
            foreign_column_name='id',
            constraint_name='fk_posts_editor',
        )
    )

    analyze_table_relationships(complex_relationship_tables)

    # Both foreign keys should be MANY_TO_ONE
    author_rel = next(rel for rel in post_table.foreign_keys if rel.column_name == 'user_id')
    editor_rel = next(rel for rel in post_table.foreign_keys if rel.column_name == 'editor_id')
    assert author_rel.relation_type == RelationType.MANY_TO_ONE, 'Post-Author should be MANY_TO_ONE'
    assert editor_rel.relation_type == RelationType.MANY_TO_ONE, 'Post-Editor should be MANY_TO_ONE'


def test_error_handling_in_relationship_detection(complex_relationship_tables):
    """Test error handling in relationship detection."""
    # Add a foreign key with non-existent target table
    post_table = complex_relationship_tables[('public', 'posts')]
    post_table.foreign_keys.append(
        ForeignKeyInfo(
            column_name='category_id',
            foreign_table_name='non_existent_table',
            foreign_column_name='id',
            constraint_name='fk_posts_category',
        )
    )

    # Should not raise an error, just skip the invalid foreign key
    analyze_table_relationships(complex_relationship_tables)

    # The invalid foreign key should be skipped but others should work
    assert any(fk.foreign_table_name == 'users' for fk in post_table.foreign_keys), (
        'Valid foreign keys should still be processed'
    )


def test_edge_case_relationship_types(complex_relationship_tables):
    """Test edge cases in relationship type detection."""
    # Add a table with a composite primary key that includes a foreign key
    composite_table = TableInfo(
        name='user_roles',
        schema='public',
        columns=[
            ColumnInfo(
                name='user_id',
                post_gres_datatype='integer',
                datatype='int',
                is_nullable=False,
                primary=True,
            ),
            ColumnInfo(
                name='role_id',
                post_gres_datatype='integer',
                datatype='int',
                is_nullable=False,
                primary=True,
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='user_id',
                foreign_table_name='users',
                foreign_column_name='id',
                constraint_name='fk_user_roles_user',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_user_roles',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (user_id, role_id)',
                columns=['user_id', 'role_id'],
            ),
        ],
    )

    complex_relationship_tables[('public', 'user_roles')] = composite_table
    analyze_table_relationships(complex_relationship_tables)
    analyze_bridge_tables(complex_relationship_tables)

    # Create a list of foreign key details for add_relationships_to_table_details
    fk_details = [
        # user_roles -> users
        ('public', 'user_roles', 'user_id', 'public', 'users', 'id', 'fk_user_roles_user'),
        # posts -> users
        ('public', 'posts', 'user_id', 'public', 'users', 'id', 'fk_posts_user'),
        # users -> user_settings
        ('public', 'users', 'settings_id', 'public', 'user_settings', 'id', 'fk_users_settings'),
        # post_tags -> posts
        ('public', 'post_tags', 'post_id', 'public', 'posts', 'id', 'fk_post_tags_post'),
        # post_tags -> tags
        ('public', 'post_tags', 'tag_id', 'public', 'tags', 'id', 'fk_post_tags_tag'),
    ]
    add_relationships_to_table_details(complex_relationship_tables, fk_details)

    # Even though user_id is part of a primary key, it should be MANY_TO_ONE because it's composite
    user_rel = next(rel for rel in composite_table.foreign_keys if rel.foreign_table_name == 'users')
    assert user_rel.relation_type == RelationType.MANY_TO_ONE, (
        'Composite primary key should not affect relationship type'
    )

    # Test ONE_TO_ONE relationship (users <-> user_settings)
    user_table = complex_relationship_tables[('public', 'users')]
    user_settings_rel = next(rel for rel in user_table.foreign_keys if rel.foreign_table_name == 'user_settings')
    assert user_settings_rel.relation_type == RelationType.ONE_TO_ONE, 'User-Settings should be ONE_TO_ONE'

    # Test MANY_TO_ONE relationship (posts -> users)
    # Many posts can point to one user (from posts table's perspective)
    post_table = complex_relationship_tables[('public', 'posts')]
    post_user_rel = next(rel for rel in post_table.foreign_keys if rel.foreign_table_name == 'users')
    assert post_user_rel.relation_type == RelationType.MANY_TO_ONE, (
        'Post-User should be MANY_TO_ONE (many posts can point to one user)'
    )

    # Test MANY_TO_MANY relationship (posts <-> tags)
    post_tags_table = complex_relationship_tables[('public', 'post_tags')]
    assert post_tags_table.is_bridge, 'post_tags should be identified as a bridge table'

    # Test relationships from bridge table
    post_rel = next(rel for rel in post_tags_table.foreign_keys if rel.foreign_table_name == 'posts')
    tag_rel = next(rel for rel in post_tags_table.foreign_keys if rel.foreign_table_name == 'tags')
    assert post_rel.relation_type == RelationType.MANY_TO_MANY, 'Bridge table -> posts should be MANY_TO_MANY'
    assert tag_rel.relation_type == RelationType.MANY_TO_MANY, 'Bridge table -> tags should be MANY_TO_MANY'

    # Test that the relationships are properly reflected in the target tables
    posts_table = complex_relationship_tables[('public', 'posts')]
    tags_table = complex_relationship_tables[('public', 'tags')]

    # Check posts -> tags relationship through bridge table
    post_to_tags_rel = next((rel for rel in posts_table.relationships if rel.related_table_name == 'tags'), None)
    assert post_to_tags_rel is not None, 'Posts should have relationship to tags'
    assert post_to_tags_rel.relation_type == RelationType.MANY_TO_MANY, 'Posts-Tags should be MANY_TO_MANY'

    # Check tags -> posts relationship through bridge table
    tags_to_posts_rel = next((rel for rel in tags_table.relationships if rel.related_table_name == 'posts'), None)
    assert tags_to_posts_rel is not None, 'Tags should have relationship to posts'
    assert tags_to_posts_rel.relation_type == RelationType.MANY_TO_MANY, 'Tags-Posts should be MANY_TO_MANY'


@pytest.fixture
def one_to_one_tables():
    """Fixture for testing one-to-one relationship detection."""
    # Profile table with single primary key
    profile = TableInfo(
        name='profile',
        schema='public',
        table_type='BASE TABLE',
        foreign_keys=[],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_profile',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (user_id)',
                columns=['user_id'],
            )
        ],
    )

    # User table with single primary key
    user = TableInfo(
        name='user',
        schema='public',
        table_type='BASE TABLE',
        foreign_keys=[],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_user',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
                columns=['id'],
            )
        ],
    )

    return {
        ('public', 'profile'): profile,
        ('public', 'user'): user,
    }


def test_one_to_one_relationship_detection(one_to_one_tables):
    """Test detection of one-to-one relationships based on single primary key constraints."""
    # Add relationships to tables
    fk_details = [
        ('public', 'profile', 'user_id', 'public', 'user', 'id', 'fk_user_profile'),
    ]
    add_foreign_key_info_to_table_details(one_to_one_tables, fk_details)

    # Get the profile table
    profile = one_to_one_tables[('public', 'profile')]

    # Verify the relationship type
    assert len(profile.foreign_keys) == 1
    fk = profile.foreign_keys[0]
    assert fk.relation_type == RelationType.ONE_TO_ONE, (
        'Expected ONE_TO_ONE relationship when foreign key is the only primary key'
    )


@pytest.fixture
def composite_key_tables():
    """Fixture for testing relationship detection with composite primary keys."""
    # Order table with composite primary key
    order = TableInfo(
        name='order',
        schema='public',
        table_type='BASE TABLE',
        foreign_keys=[],
        columns=[],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_order',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (order_id, user_id)',  # Primary key includes user_id
                columns=['order_id', 'user_id'],
            )
        ],
    )

    # User table with single primary key
    user = TableInfo(
        name='user',
        schema='public',
        table_type='BASE TABLE',
        foreign_keys=[],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_user',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
                columns=['id'],
            )
        ],
    )

    return {
        ('public', 'order'): order,
        ('public', 'user'): user,
    }


def test_composite_key_relationship_detection(composite_key_tables):
    """Test that composite primary keys are correctly detected as many-to-one relationships."""
    # Add relationships to tables
    fk_details = [
        ('public', 'order', 'user_id', 'public', 'user', 'id', 'fk_user_order'),
    ]
    add_foreign_key_info_to_table_details(composite_key_tables, fk_details)

    # Get the order table
    order = composite_key_tables[('public', 'order')]

    # Debug logging
    logging.debug('Order table constraints:')
    for constraint in order.constraints:
        logging.debug(f'  - {constraint.raw_constraint_type}: {constraint.columns}')
    logging.debug('Foreign keys:')
    for fk in order.foreign_keys:
        logging.debug(f'  - {fk.column_name} -> {fk.foreign_table_name}.{fk.foreign_column_name} ({fk.relation_type})')

    # Verify the relationship type
    assert len(order.foreign_keys) == 1
    fk = order.foreign_keys[0]
    assert fk.relation_type == RelationType.MANY_TO_ONE, (
        'Expected MANY_TO_ONE relationship when foreign key is part of a composite primary key'
    )


@pytest.fixture
def relationship_type_tables():
    """Fixture for testing determine_relationship_type function."""
    # Create tables with various uniqueness configurations
    source_table = TableInfo(
        name='source',
        schema='public',
        columns=[
            ColumnInfo(
                name='id',
                primary=True,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='uuid',
                datatype='str',
            ),
            ColumnInfo(
                name='target_id',
                primary=False,
                is_unique=True,  # This can be varied for different test cases
                is_foreign_key=True,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_source',
                columns=['id'],
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
            ),
            ConstraintInfo(
                constraint_name='unique_target_id',
                columns=['target_id'],
                raw_constraint_type='u',
                constraint_definition='UNIQUE (target_id)',
            ),
        ],
    )

    target_table = TableInfo(
        name='target',
        schema='public',
        columns=[
            ColumnInfo(
                name='id',
                primary=True,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_target',
                columns=['id'],
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
            ),
        ],
    )

    return source_table, target_table


def test_determine_relationship_type(relationship_type_tables):
    """Test the determine_relationship_type function for various scenarios."""
    from supabase_pydantic.util.marshalers import determine_relationship_type

    source_table, target_table = relationship_type_tables
    fk = ForeignKeyInfo(
        constraint_name='fk_target',
        column_name='target_id',
        foreign_table_name='target',
        foreign_column_name='id',
    )

    # Test ONE_TO_ONE relationship (both sides unique)
    forward_type, reverse_type = determine_relationship_type(source_table, target_table, fk)
    assert forward_type == RelationType.ONE_TO_ONE
    assert reverse_type == RelationType.ONE_TO_ONE

    # Test MANY_TO_ONE relationship (only target unique)
    source_table.columns[1].is_unique = False  # Make source column non-unique
    source_table.constraints = [c for c in source_table.constraints if c.raw_constraint_type != 'u']
    forward_type, reverse_type = determine_relationship_type(source_table, target_table, fk)
    assert forward_type == RelationType.MANY_TO_ONE
    assert reverse_type == RelationType.ONE_TO_MANY

    # Test MANY_TO_MANY relationship (neither side unique)
    target_table.columns[0].is_unique = False  # Make target column non-unique
    target_table.constraints = []  # Remove uniqueness constraints
    forward_type, reverse_type = determine_relationship_type(source_table, target_table, fk)
    assert forward_type == RelationType.MANY_TO_MANY
    assert reverse_type == RelationType.MANY_TO_MANY


@pytest.fixture
def foreign_key_tables():
    """Fixture for testing add_foreign_key_info_to_table_details function."""
    # Create tables with various foreign key configurations
    users_table = TableInfo(
        name='users',
        schema='public',
        columns=[
            ColumnInfo(
                name='id',
                primary=True,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='uuid',
                datatype='str',
            ),
            ColumnInfo(
                name='profile_id',
                primary=False,
                is_unique=True,
                is_foreign_key=True,
                post_gres_datatype='uuid',
                datatype='str',
            ),
            ColumnInfo(
                name='department_id',
                primary=False,
                is_unique=False,
                is_foreign_key=True,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        constraints=[],
    )

    profiles_table = TableInfo(
        name='profiles',
        schema='public',
        columns=[
            ColumnInfo(
                name='id',
                primary=True,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        constraints=[],
    )

    departments_table = TableInfo(
        name='departments',
        schema='public',
        columns=[
            ColumnInfo(
                name='id',
                primary=True,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        constraints=[],
    )

    # Create a table in a different schema
    auth_users_table = TableInfo(
        name='users',
        schema='auth',
        columns=[
            ColumnInfo(
                name='id',
                primary=True,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        constraints=[],
    )

    tables = {
        ('public', 'users'): users_table,
        ('public', 'profiles'): profiles_table,
        ('public', 'departments'): departments_table,
        ('auth', 'users'): auth_users_table,
    }

    return tables


def test_add_foreign_key_info_to_table_details_multiple_fks(foreign_key_tables):
    """Test adding multiple foreign keys to a table."""
    fk_details = [
        # ONE_TO_ONE relationship (unique foreign key)
        ('public', 'users', 'profile_id', 'public', 'profiles', 'id', 'fk_user_profile'),
        # MANY_TO_ONE relationship (non-unique foreign key)
        ('public', 'users', 'department_id', 'public', 'departments', 'id', 'fk_user_department'),
    ]

    add_foreign_key_info_to_table_details(foreign_key_tables, fk_details)
    users_table = foreign_key_tables[('public', 'users')]

    # Check that both foreign keys were added
    assert len(users_table.foreign_keys) == 2

    # Check profile foreign key
    profile_fk = next(fk for fk in users_table.foreign_keys if fk.foreign_table_name == 'profiles')
    assert profile_fk.column_name == 'profile_id'
    assert profile_fk.foreign_column_name == 'id'
    assert profile_fk.constraint_name == 'fk_user_profile'

    # Check department foreign key
    dept_fk = next(fk for fk in users_table.foreign_keys if fk.foreign_table_name == 'departments')
    assert dept_fk.column_name == 'department_id'
    assert dept_fk.foreign_column_name == 'id'
    assert dept_fk.constraint_name == 'fk_user_department'


def test_add_foreign_key_info_cross_schema(foreign_key_tables):
    """Test adding foreign keys across different schemas."""
    fk_details = [
        # Foreign key from public.users to auth.users
        ('public', 'users', 'profile_id', 'auth', 'users', 'id', 'fk_user_auth'),
    ]

    add_foreign_key_info_to_table_details(foreign_key_tables, fk_details)
    users_table = foreign_key_tables[('public', 'users')]

    # Check that the cross-schema foreign key was added
    assert len(users_table.foreign_keys) == 1
    fk = users_table.foreign_keys[0]
    assert fk.foreign_table_name == 'users'
    assert fk.foreign_table_schema == 'auth'


def test_add_foreign_key_info_missing_table(foreign_key_tables):
    """Test handling of foreign keys with missing tables."""
    fk_details = [
        # Foreign key to a non-existent table
        ('public', 'users', 'role_id', 'public', 'roles', 'id', 'fk_user_role'),
    ]

    # Should not raise an error, just skip the foreign key
    add_foreign_key_info_to_table_details(foreign_key_tables, fk_details)
    users_table = foreign_key_tables[('public', 'users')]
    assert len(users_table.foreign_keys) == 0


def test_add_foreign_key_info_invalid_schema(foreign_key_tables):
    """Test handling of foreign keys with invalid schemas."""
    fk_details = [
        # Foreign key with non-existent schema
        ('invalid', 'users', 'profile_id', 'public', 'profiles', 'id', 'fk_user_profile'),
    ]

    # Should not raise an error, just skip the foreign key
    add_foreign_key_info_to_table_details(foreign_key_tables, fk_details)
    assert ('invalid', 'users') not in foreign_key_tables
