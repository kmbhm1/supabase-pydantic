"""Tests for database graph utilities in supabase_pydantic.db.graph."""

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.models import ForeignKeyInfo, RelationshipInfo, TableInfo
from supabase_pydantic.db.graph import (
    build_dependency_graph,
    reorganize_tables_by_relationships,
    separate_tables_list_by_type,
    sort_tables_by_in_degree,
    sort_tables_for_insert,
    topological_sort,
)


import pytest


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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
def test_separate_tables_list_by_type_all_views():
    tables = [TableInfo(name='A', table_type='VIEW'), TableInfo(name='B', table_type='VIEW')]
    table_list = ['A', 'B']

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == []
    assert views == ['A', 'B']


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
def test_separate_tables_list_by_type_all_base_tables():
    tables = [TableInfo(name='A', table_type='BASE_TABLE'), TableInfo(name='B', table_type='BASE_TABLE')]
    table_list = ['A', 'B']

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == ['A', 'B']
    assert views == []


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
def test_separate_tables_list_by_type_table_not_found():
    tables = [TableInfo(name='A', table_type='BASE_TABLE'), TableInfo(name='B', table_type='VIEW')]
    table_list = ['A', 'B', 'C']  # "C" is not in tables

    base_tables, views = separate_tables_list_by_type(tables, table_list)

    assert base_tables == ['A']
    assert views == ['B']


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.graph
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
