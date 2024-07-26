import pytest
import subprocess
from supabase_pydantic.util.sorting import run_isort, get_graph_from_tables, topological_sort
from supabase_pydantic.util.dataclasses import ForeignKeyInfo, TableInfo


def test_run_isort_success(mocker, capsys):
    """Test run_isort succeeds without errors."""
    mocker.patch('subprocess.run')
    subprocess.run.return_value = subprocess.CompletedProcess(
        args=['isort', 'dummy_file.py'], returncode=0, stdout='Done', stderr=''
    )

    run_isort('dummy_file.py')
    out, err = capsys.readouterr()
    assert err == '' or err is None


# def test_run_isort_failure(mocker, capsys):
#     """Test run_isort handles CalledProcessError correctly."""
#     error_output = 'An error occurred'
#     mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'isort', stderr=error_output))

#     run_isort('non_existent_file.py')
#     out, err = capsys.readouterr()
#     # assert 'An error occurred while running isort:' in out
#     assert error_output in err


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
    assert graph == {'table1': ['table2']}
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

    with pytest.raises(ValueError) as excinfo:
        topological_sort(tables)


def test_topological_sort_with_cycle():
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
