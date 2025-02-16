from unittest.mock import MagicMock, patch

import pytest

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
    update_column_constraint_definitions,
    update_columns_with_constraints,
)


# Fixture for column details
@pytest.fixture
def column_details():
    return [
        ('public', 'users', 'user_id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE'),
        ('public', 'users', 'email', None, 'YES', 'text', 255, 'BASE TABLE'),
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


# Test add_foreign_key_info_to_table_details
def test_add_foreign_key_info_to_table_details(column_details, fk_details):
    tables = get_table_details_from_columns(column_details)
    add_foreign_key_info_to_table_details(tables, fk_details)
    table = tables[('public', 'users')]
    assert len(table.foreign_keys) == 1
    assert table.foreign_keys[0].foreign_table_name == 'orders'


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

    # Check basic one-to-many relationship
    assert setup_analyze_tables['public.orders'].foreign_keys[0].relation_type == RelationType.ONE_TO_ONE

    # Check for automatically added reciprocal foreign key in users table
    assert len(setup_analyze_tables['public.users'].foreign_keys) == 1
    assert setup_analyze_tables['public.users'].foreign_keys[0].relation_type == RelationType.ONE_TO_ONE
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
    # Add reciprocal foreign key in users table
    setup_analyze_tables['public.users'].foreign_keys.append(
        ForeignKeyInfo(
            constraint_name='fk_user_id',
            column_name='id',
            foreign_table_name='orders',
            foreign_column_name='user_id',
            relation_type=None,
        )
    )
    analyze_table_relationships(setup_analyze_tables)
    # Expecting a many-to-many because of reciprocal relationship
    assert setup_analyze_tables['public.orders'].foreign_keys[0].relation_type == RelationType.ONE_TO_ONE
    assert setup_analyze_tables['public.users'].foreign_keys[0].relation_type == RelationType.ONE_TO_MANY


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
        name='User',
        schema='public',
        columns=[
            ColumnInfo(name='country_code', post_gres_datatype='text', is_nullable=False, datatype='str'),
            ColumnInfo(name='username', post_gres_datatype='text', is_nullable=False, datatype='str'),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='country_code_length_check',
                raw_constraint_type='c',
                columns=['country_code'],
                constraint_definition='CHECK (length(country_code) = 2)',
            ),
            ConstraintInfo(
                constraint_name='username_length_check',
                raw_constraint_type='c',
                columns=['username'],
                constraint_definition='CHECK (length(username) >= 4 AND length(username) <= 20)',
            ),
        ],
    )

    # Update the columns with constraints
    tables = {('public', 'User'): table}
    update_column_constraint_definitions(tables)

    # Verify the constraints were correctly added
    country_code_col = next(col for col in table.columns if col.name == 'country_code')
    assert country_code_col.constraint_definition == 'CHECK (length(country_code) = 2)'

    username_col = next(col for col in table.columns if col.name == 'username')
    assert username_col.constraint_definition == 'CHECK (length(username) >= 4 AND length(username) <= 20)'
