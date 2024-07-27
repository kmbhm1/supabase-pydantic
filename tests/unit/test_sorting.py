import pytest
import subprocess
from supabase_pydantic.util.sorting import format_with_ruff, run_isort, get_graph_from_tables, topological_sort
from supabase_pydantic.util.dataclasses import ForeignKeyInfo, TableInfo


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


def test_get_graph_from_tables_empty():
    """Test with no tables."""
    tables = []
    graph, indegree = get_graph_from_tables(tables)
    assert graph == {}
    assert indegree == {}


def test_get_graph_from_tables():
    """Test normal functionality."""
    tables = [
        TableInfo(
            name='table1',
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='fk_table1_table2',
                    column_name='table1_id',
                    foreign_table_name='table2',
                    foreign_column_name='table2_id',
                )
            ],
        ),
        TableInfo(name='table2', foreign_keys=[]),
    ]
    graph, indegree = get_graph_from_tables(tables)
    assert graph == {'table2': ['table1']}
    assert indegree == {'table1': 1, 'table2': 0}


def test_topological_sort_no_cycle():
    """Test sorting without a cycle."""
    tables = [
        TableInfo(
            name='table1',
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='fk_table1_table2',
                    column_name='table1_id',
                    foreign_table_name='table2',
                    foreign_column_name='table2_id',
                )
            ],
        ),
        TableInfo(name='table2', foreign_keys=[]),
    ]

    result = topological_sort(tables)
    assert [table.name for table in result] == ['table2', 'table1']


def test_topological_sort_with_cycle_causes_error():
    """Test detection of cycle."""
    tables = [
        TableInfo(
            name='table1',
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='fk_table1_table2',
                    column_name='table1_id',
                    foreign_table_name='table2',
                    foreign_column_name='table2_id',
                )
            ],
        ),
        TableInfo(
            name='table2',
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='fk_table2_table1',
                    column_name='table2_id',
                    foreign_table_name='table1',
                    foreign_column_name='table1_id',
                )
            ],
        ),
    ]
    with pytest.raises(ValueError) as excinfo:
        topological_sort(tables)
    assert 'Cycle detected in the graph' in str(excinfo.value)


def test_topological_sort_success():
    """Test topological sort successfully orders tables without a cycle."""
    tables = [
        TableInfo(
            name='table1',
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='fk_table1_table3',
                    column_name='table1_id',
                    foreign_table_name='table3',
                    foreign_column_name='table3_id',
                )
            ],
        ),
        TableInfo(name='table2', foreign_keys=[]),
        TableInfo(
            name='table3',
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='fk_table3_table2',
                    column_name='table3_id',
                    foreign_table_name='table2',
                    foreign_column_name='table2_id',
                )
            ],
        ),
    ]
    sorted_tables = topological_sort(tables)
    # Verify that tables are sorted in a valid topological order
    sorted_table_names = [table.name for table in sorted_tables]
    assert sorted_table_names == [
        'table2',
        'table3',
        'table1',
    ], f"Expected ['table2', 'table3', 'table1'], got {sorted_table_names}"


def test_topological_sort_multiple_trees():
    """Test topological sort with multiple independent dependency trees."""
    tables = [
        TableInfo(name='table1', foreign_keys=[]),
        TableInfo(
            name='table2',
            foreign_keys=[ForeignKeyInfo('fk_table2_table4', 'id', 'table4', 'id')],
        ),
        TableInfo(name='table3', foreign_keys=[]),
        TableInfo(name='table4', foreign_keys=[]),
    ]
    sorted_tables = topological_sort(tables)
    # This test may have multiple valid outputs due to independent trees
    assert set(table.name for table in sorted_tables) == {'table1', 'table2', 'table3', 'table4'}


def test_topological_sort_single_table():
    """Test topological sort with a single table, no dependencies."""
    tables = [TableInfo(name='table1', foreign_keys=[])]
    sorted_tables = topological_sort(tables)
    assert sorted_tables == tables  # The single table remains in its position
