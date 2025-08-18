"""Tests for seed data generation functions in supabase_pydantic.db.seed.generator."""

from math import inf
from unittest.mock import Mock, patch
import pytest

from supabase_pydantic.db.models import (
    ColumnInfo,
    ConstraintInfo,
    ForeignKeyInfo,
    TableInfo,
)
from supabase_pydantic.db.seed.generator import (
    generate_seed_data,
    pick_random_foreign_key,
    total_possible_combinations,
    unique_data_rows,
)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
@patch('random.random', return_value=0.5)  # Control the number of rows
@patch('random.choice', side_effect=lambda x: x[0])  # Control choice function
@patch(
    'supabase_pydantic.db.seed.fake.generate_fake_data',
    side_effect=lambda datatype, nullable, max_length, name: f'fake_{name}',
)
def test_generate_seed_data(mock_generate_fake_data, mock_choice, mock_random):
    # Define the columns and foreign keys
    columns_a = [
        ColumnInfo(name='id', post_gres_datatype='integer', datatype='int4', primary=True),
        ColumnInfo(name='name', post_gres_datatype='text', datatype='str', is_unique=False),
    ]

    columns_b = [
        ColumnInfo(name='id', post_gres_datatype='integer', datatype='int4', primary=True),
        ColumnInfo(name='a_id', post_gres_datatype='integer', datatype='int4', is_foreign_key=True),
    ]

    foreign_keys_b = [
        ForeignKeyInfo(column_name='a_id', foreign_table_name='A', foreign_column_name='id', constraint_name='foo')
    ]

    # Define the tables
    table_a = TableInfo(name='A', columns=columns_a)
    table_b = TableInfo(name='B', columns=columns_b, foreign_keys=foreign_keys_b)

    tables = [table_a, table_b]

    # Call the function
    seed_data = generate_seed_data(tables)

    # Expected seed data structure
    expected_seed_data = {
        'A': [['id', 'name'], ['fake_id', 'fake_name'], ['fake_id', 'fake_name']],
        'B': [['id', 'a_id'], ['fake_id', 'fake_id'], ['fake_id', 'fake_id']],
    }

    # assert seed_data == expected_seed_data
    assert seed_data.keys() == expected_seed_data.keys()
    assert seed_data['A'][0] == expected_seed_data['A'][0]
    assert seed_data['B'][0] == expected_seed_data['B'][0]

    for i in range(1, len(seed_data['A'])):
        assert str(seed_data['A'][i][0]).isnumeric() or seed_data['A'][i][0] == 'NULL'
        assert str(seed_data['A'][i][1]).isalpha or seed_data['A'][i][0] == 'NULL'

    for i in range(1, len(seed_data['B'])):
        assert str(seed_data['B'][i][0]).isnumeric() or seed_data['B'][i][0] == 'NULL'
        assert str(seed_data['B'][i][1]).isnumeric() or seed_data['B'][i][1] == 'NULL'


@pytest.fixture
def table_with_unique_columns():
    return TableInfo(
        name='C',
        columns=[
            ColumnInfo(
                name='id',
                user_defined_values=['1', '2', '3'],
                is_unique=True,
                datatype='int4',
                post_gres_datatype='integer',
            ),
            ColumnInfo(
                name='type', user_defined_values=['A', 'B'], is_unique=True, datatype='str', post_gres_datatype='text'
            ),
        ],
    )


@pytest.fixture
def table_with_infinite_possible_values():
    return TableInfo(
        name='A',
        columns=[
            ColumnInfo(
                name='id', user_defined_values=None, is_unique=True, datatype='int4', post_gres_datatype='integer'
            ),
        ],
    )


@pytest.fixture
def table_with_no_unique_constraints():
    return TableInfo(
        name='B',
        columns=[
            ColumnInfo(
                name='id',
                user_defined_values=['1', '2', '3'],
                is_unique=False,
                datatype='int4',
                post_gres_datatype='integer',
            )
        ],
    )


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
def test_pick_random_foreign_key():
    # Mock the remember_fn
    remember_fn = Mock()

    # Create mock foreign key info
    fk_info = ForeignKeyInfo(
        constraint_name='fk_constraint',
        column_name='fk_column',
        foreign_table_name='foreign_table',
        foreign_column_name='foreign_column',
        foreign_table_schema='public',
    )
    table_info = TableInfo(name='table', foreign_keys=[fk_info])

    # Set up the remember_fn to return a list of values for the foreign key
    remember_fn.return_value = {1, 2, 3, 4}

    # Test that a valid foreign key value is returned
    result = pick_random_foreign_key('fk_column', table_info, remember_fn)
    assert result in {1, 2, 3, 4}, 'Expected one of the foreign key values to be returned'

    # Test for a column without a foreign key
    result = pick_random_foreign_key('non_existing_column', table_info, remember_fn)
    assert result == 'NULL', "Expected 'NULL' when no foreign key is found"

    # Test when remember_fn raises KeyError
    remember_fn.side_effect = KeyError
    result = pick_random_foreign_key('fk_column', table_info, remember_fn)
    assert result == 'NULL', "Expected 'NULL' when remember_fn raises KeyError"


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
def test_total_possible_combinations():
    # Test case where table has unique constraint with user-defined values
    column_info_1 = ColumnInfo(
        name='id', is_unique=True, user_defined_values=[1, 2, 3], datatype='int4', post_gres_datatype='integer'
    )
    column_info_2 = ColumnInfo(
        name='type', datatype='str', post_gres_datatype='text', is_unique=True, user_defined_values=['a', 'b']
    )
    constraint = ConstraintInfo(raw_constraint_type='u', constraint_name='unique_constraint', constraint_definition='')
    table_info = TableInfo(name='table', columns=[column_info_1, column_info_2], constraints=[constraint])

    result = total_possible_combinations(table_info)
    expected = float(3 * 2)  # 3 options for column 1, 2 options for column 2
    assert result == expected, f'Expected {expected} but got {result}'

    # Test case where table has a unique constraint but no user-defined values
    column_info_3 = ColumnInfo(name='foo', is_unique=True, datatype='int4', post_gres_datatype='integer')
    table_info_no_values = TableInfo(name='test', columns=[column_info_3])

    result = total_possible_combinations(table_info_no_values)
    assert result == inf, "Expected 'inf' when a unique column has no user-defined values"

    # Test case where table has no unique constraint
    column_info_4 = ColumnInfo(name='bar', is_unique=False, datatype='int4', post_gres_datatype='integer')
    table_info_no_unique = TableInfo(name='test', columns=[column_info_4])

    result = total_possible_combinations(table_info_no_unique)
    assert result == inf, "Expected 'inf' when the table has no unique constraint"


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
def test_unique_data_rows_no_unique_constraints():
    table = TableInfo(
        name='test_table',
        columns=[ColumnInfo(name='id', datatype='int4', post_gres_datatype='integer', is_unique=False)],
        constraints=[],
    )
    result = unique_data_rows(table, remember_fn=Mock())
    assert result == []


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
def test_unique_data_rows_finite_combinations():
    table = TableInfo(
        name='test_table',
        columns=[
            ColumnInfo(
                name='id',
                datatype='int4',
                post_gres_datatype='integer',
                is_unique=True,
                user_defined_values=['1', '2', '3'],
            ),
            ColumnInfo(
                name='name',
                datatype='str',
                post_gres_datatype='text',
                is_unique=True,
                user_defined_values=['Alice', 'Bob'],
            ),
        ],
        constraints=[
            ConstraintInfo(
                raw_constraint_type='u',
                constraint_name='unique_constraint',
                constraint_definition='',
                columns=['id', 'name'],
            )
        ],
    )
    result = unique_data_rows(table, remember_fn=Mock())
    assert len(result) == 6  # Since there are 6 possible unique combinations


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
def test_unique_data_rows_infinite_combinations():
    table = TableInfo(
        name='test_table',
        columns=[
            ColumnInfo(
                name='id', datatype='int4', post_gres_datatype='integer', is_unique=True, user_defined_values=[]
            ),
            ColumnInfo(name='name', datatype='str', post_gres_datatype='text', is_unique=True, user_defined_values=[]),
        ],
        constraints=[
            ConstraintInfo(
                raw_constraint_type='u',
                constraint_name='unique_constraint',
                constraint_definition='',
                columns=['id', 'name'],
            )
        ],
    )
    result = unique_data_rows(table, remember_fn=Mock())
    assert len(result) > 0  # Should generate some rows even with infinite possibilities


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.seed
def test_unique_data_rows_with_foreign_keys():
    table = TableInfo(
        name='test_table',
        columns=[
            ColumnInfo(name='id', datatype='int4', post_gres_datatype='integer', is_unique=True, is_foreign_key=True),
            ColumnInfo(
                name='name',
                datatype='str',
                post_gres_datatype='text',
                is_unique=True,
                user_defined_values=['Alice', 'Bob'],
            ),
        ],
        constraints=[
            ConstraintInfo(
                raw_constraint_type='u',
                constraint_name='unique_constraint',
                constraint_definition='',
                columns=['id', 'name'],
            )
        ],
    )
    with patch('supabase_pydantic.db.seed.generator.pick_random_foreign_key', return_value=1):
        result = unique_data_rows(table, remember_fn=Mock())
    assert len(result) == 2  # Should generate 2 rows, one for each name
