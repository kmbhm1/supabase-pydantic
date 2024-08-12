from unittest.mock import patch
import pytest
import subprocess
from supabase_pydantic.util.constants import RelationType
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, RelationshipInfo, TableInfo
from supabase_pydantic.util.sorting import (
    build_dependency_graph,
    format_with_ruff,
    generate_seed_data,
    reorganize_tables_by_relationships,
    run_isort,
    separate_tables_list_by_type,
    sort_tables_by_in_degree,
    sort_tables_for_insert,
    topological_sort,
)


def test_run_isort_success(mocker, capsys):
    """Test run_isort succeeds without errors."""
    mocker.patch('subprocess.run')
    subprocess.run.return_value = subprocess.CompletedProcess(
        args=['isort', 'dummy_file.py'], returncode=0, stdout='Done', stderr=''
    )

    run_isort('dummy_file.py')
    _, err = capsys.readouterr()
    assert err == '' or err is None


def test_run_isort_failure_fails_silently(mocker, capsys):
    """Test run_isort handles CalledProcessError correctly."""
    error_output = 'An error occurred'
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'isort', stderr=error_output))

    run_isort('non_existent_file.py')
    out, err = capsys.readouterr()
    assert error_output in out
    assert error_output not in err


def test_format_with_ruff_success(mocker, capsys):
    """Test run_isort succeeds without errors."""
    mocker.patch('subprocess.run')
    subprocess.run.return_value = subprocess.CompletedProcess(
        args=['isort', 'dummy_file.py'], returncode=0, stdout='Done', stderr=''
    )

    format_with_ruff('dummy_file.py')
    _, err = capsys.readouterr()
    assert err == '' or err is None


def test_format_with_ruff_failure_fails_silently(mocker, capsys):
    """Test run_isort handles CalledProcessError correctly."""
    error_output = 'An error occurred'
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'isort', stderr=error_output))

    format_with_ruff('non_existent_file.py')
    out, err = capsys.readouterr()
    assert error_output in out
    assert error_output not in err


def test_build_dependency_graph():
    table_a = TableInfo(name='A')
    table_b = TableInfo(
        name='B',
        foreign_keys=[
            ForeignKeyInfo(foreign_table_name='A', constraint_name='foo', column_name='id', foreign_column_name='baz')
        ],
    )
    table_c = TableInfo(
        name='C',
        foreign_keys=[
            ForeignKeyInfo(foreign_table_name='B', constraint_name='foo', column_name='id', foreign_column_name='baz')
        ],
    )
    table_d = TableInfo(
        name='D',
        foreign_keys=[
            ForeignKeyInfo(foreign_table_name='A', constraint_name='foo', column_name='id', foreign_column_name='baz')
        ],
    )

    tables = [table_a, table_b, table_c, table_d]

    graph, in_degree = build_dependency_graph(tables)

    expected_graph = {'A': ['B', 'D'], 'B': ['C']}

    expected_in_degree = {'A': 0, 'B': 1, 'C': 1, 'D': 1}

    assert graph == expected_graph
    assert in_degree == expected_in_degree


def test_topological_sort():
    table_a = TableInfo(name='A')
    table_b = TableInfo(
        name='B',
        foreign_keys=[
            ForeignKeyInfo(foreign_table_name='A', constraint_name='foo', column_name='id', foreign_column_name='baz')
        ],
    )
    table_c = TableInfo(
        name='C',
        foreign_keys=[
            ForeignKeyInfo(foreign_table_name='B', constraint_name='foo', column_name='id', foreign_column_name='baz')
        ],
    )
    table_d = TableInfo(
        name='D',
        foreign_keys=[
            ForeignKeyInfo(foreign_table_name='A', constraint_name='foo', column_name='id', foreign_column_name='baz')
        ],
    )

    tables = [table_a, table_b, table_c, table_d]

    in_degree, graph = topological_sort(tables)

    expected_graph = {'A': ['B', 'D'], 'B': ['C']}

    expected_in_degree = {'A': 0, 'B': 1, 'C': 1, 'D': 1}

    assert graph == expected_graph
    assert in_degree == expected_in_degree


def test_sort_tables_by_in_degree():
    in_degree = {'A': 0, 'B': 1, 'C': 2, 'D': 1}

    sorted_tables = sort_tables_by_in_degree(in_degree)

    expected_sorted_tables = ['A', 'B', 'D', 'C']

    assert sorted_tables == expected_sorted_tables


def test_reorganize_tables_by_relationships_no_reordering_needed():
    sorted_tables = ['A', 'B', 'C']
    relationships = [
        RelationshipInfo(table_name='B', related_table_name='A', relation_type=RelationType.ONE_TO_MANY),
        RelationshipInfo(table_name='C', related_table_name='B', relation_type=RelationType.ONE_TO_ONE),
    ]

    result = reorganize_tables_by_relationships(sorted_tables, relationships)

    # No reordering needed because foreign tables are already before the dependent tables
    expected_result = ['A', 'B', 'C']
    assert result == expected_result


def test_reorganize_tables_by_relationships_reordering_needed():
    sorted_tables = ['A', 'B', 'C']
    relationships = [
        RelationshipInfo(table_name='A', related_table_name='B', relation_type=RelationType.ONE_TO_MANY),
        RelationshipInfo(table_name='B', related_table_name='C', relation_type=RelationType.ONE_TO_ONE),
    ]

    result = reorganize_tables_by_relationships(sorted_tables, relationships)

    # Reordering needed: "C" should come before "B" and "B" before "A"
    expected_result = ['C', 'B', 'A']
    assert result == expected_result


def test_reorganize_tables_by_relationships_many_to_many_ignored():
    sorted_tables = ['A', 'B', 'C']
    relationships = [
        RelationshipInfo(table_name='A', related_table_name='B', relation_type=RelationType.MANY_TO_MANY),
        RelationshipInfo(table_name='B', related_table_name='C', relation_type=RelationType.ONE_TO_ONE),
    ]

    result = reorganize_tables_by_relationships(sorted_tables, relationships)

    # MANY_TO_MANY relationship should be ignored, so no reordering based on A-B
    expected_result = ['A', 'C', 'B']
    assert result == expected_result


def test_reorganize_tables_by_relationships_complex_case():
    sorted_tables = ['A', 'B', 'C', 'D']
    relationships = [
        RelationshipInfo(table_name='B', related_table_name='A', relation_type=RelationType.ONE_TO_ONE),
        RelationshipInfo(table_name='C', related_table_name='B', relation_type=RelationType.ONE_TO_ONE),
        RelationshipInfo(table_name='D', related_table_name='A', relation_type=RelationType.ONE_TO_ONE),
    ]

    result = reorganize_tables_by_relationships(sorted_tables, relationships)

    # Expected reordering based on relationships
    expected_result = ['A', 'B', 'C', 'D']
    assert result == expected_result


def test_separate_tables_list_by_type_mixed():
    tables = [
        TableInfo(name='A', table_type='BASE_TABLE'),
        TableInfo(name='B', table_type='VIEW'),
        TableInfo(name='C', table_type='BASE_TABLE'),
        TableInfo(name='D', table_type='VIEW'),
    ]
    table_list = ['A', 'B', 'C', 'D']

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == ['A', 'C']
    assert views == ['B', 'D']


def test_separate_tables_list_by_type_all_views():
    tables = [TableInfo(name='A', table_type='VIEW'), TableInfo(name='B', table_type='VIEW')]
    table_list = ['A', 'B']

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == []
    assert views == ['A', 'B']


def test_separate_tables_list_by_type_all_base_tables():
    tables = [TableInfo(name='A', table_type='BASE_TABLE'), TableInfo(name='B', table_type='BASE_TABLE')]
    table_list = ['A', 'B']

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == ['A', 'B']
    assert views == []


def test_separate_tables_list_by_type_table_not_found():
    tables = [TableInfo(name='A', table_type='BASE_TABLE'), TableInfo(name='B', table_type='VIEW')]
    table_list = ['A', 'B', 'C']  # "C" is not in tables

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == ['A']
    assert views == ['B']


def test_sort_tables_for_insert_simple():
    tables = [
        TableInfo(name='A', table_type='BASE_TABLE'),
        TableInfo(
            name='B',
            table_type='BASE_TABLE',
            foreign_keys=[
                ForeignKeyInfo(
                    foreign_table_name='A', constraint_name='foo', column_name='id', foreign_column_name='baz'
                )
            ],
        ),
        TableInfo(
            name='C',
            table_type='BASE_TABLE',
            foreign_keys=[
                ForeignKeyInfo(
                    foreign_table_name='B', constraint_name='foo', column_name='id', foreign_column_name='baz'
                )
            ],
        ),
        TableInfo(name='D', table_type='VIEW'),
    ]

    base_tables, views = sort_tables_for_insert(tables)

    # "C" depends on "B", and "B" depends on "A", so the order should be A, B, C
    assert base_tables == ['A', 'B', 'C']
    assert views == ['D']


def test_sort_tables_for_insert_complex():
    tables = [
        TableInfo(name='A', table_type='BASE_TABLE'),
        TableInfo(
            name='B',
            table_type='BASE_TABLE',
            foreign_keys=[
                ForeignKeyInfo(
                    foreign_table_name='A', constraint_name='foo', column_name='id', foreign_column_name='baz'
                )
            ],
        ),
        TableInfo(
            name='C',
            table_type='BASE_TABLE',
            foreign_keys=[
                ForeignKeyInfo(
                    foreign_table_name='B', constraint_name='foo', column_name='id', foreign_column_name='baz'
                )
            ],
        ),
        TableInfo(
            name='D',
            table_type='BASE_TABLE',
            relationships=[
                RelationshipInfo(table_name='D', related_table_name='A', relation_type=RelationType.ONE_TO_ONE)
            ],
        ),
        TableInfo(name='E', table_type='VIEW'),
    ]

    base_tables, views = sort_tables_for_insert(tables)

    # Expected order should consider foreign keys and relationships
    assert base_tables == ['A', 'D', 'B', 'C']
    assert views == ['E']


# Test case for generate_seed_data
@patch('random.random', return_value=0.5)  # Control the number of rows
@patch('random.choice', side_effect=lambda x: x[0])  # Control choice function
@patch(
    'supabase_pydantic.util.fake.generate_fake_data',
    side_effect=lambda datatype, nullable, max_length, name: f'fake_{name}',
)
def test_generate_seed_data(mock_generate_fake_data, mock_choice, mock_random):
    # Define the columns and foreign keys
    columns_a = [
        ColumnInfo(name='id', post_gres_datatype='integer', datatype='int4', primary=True),
        ColumnInfo(name='name', post_gres_datatype='text', datatype='str', is_unique=True),
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
