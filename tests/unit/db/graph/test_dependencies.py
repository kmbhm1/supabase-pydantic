"""Tests for dependency graph functions in supabase_pydantic.db.graph."""

import pytest

from supabase_pydantic.db.models import ForeignKeyInfo, TableInfo
from supabase_pydantic.db.graph import (
    build_dependency_graph,
    sort_tables_by_in_degree,
    topological_sort,
)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
def test_sort_tables_by_in_degree():
    in_degree = {'A': 0, 'B': 1, 'C': 2, 'D': 1}

    sorted_tables = sort_tables_by_in_degree(in_degree)

    expected_sorted_tables = ['A', 'B', 'D', 'C']

    assert sorted_tables == expected_sorted_tables
