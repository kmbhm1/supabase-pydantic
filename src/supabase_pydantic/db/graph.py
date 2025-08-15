import logging
from collections import defaultdict

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.models import RelationshipInfo, TableInfo

# Get Logger
logger = logging.getLogger(__name__)


def build_dependency_graph(tables: list[TableInfo]) -> tuple[defaultdict[str, list[str]], dict[str, int]]:
    """Build a dependency graph from the tables."""
    graph = defaultdict(list)
    in_degree: dict[str, int] = defaultdict(int)
    base_tables = [table for table in tables if table.table_type != 'VIEW']  # Exclude views

    # Initialize in_degree 1 for all tables
    in_degree = {table.name: 0 for table in base_tables}

    # Build the graph and in_degree dictionary
    for table in base_tables:
        for fk in table.foreign_keys:
            # fk.foreign_table_name is the table this table depends on
            graph[fk.foreign_table_name].append(table.name)
            in_degree[table.name] += 1

    return graph, in_degree


def topological_sort(tables: list[TableInfo]) -> tuple[dict, defaultdict]:
    """Topologically sort the tables based on foreign key relationships."""
    in_degree = {t.name: 0 for t in tables}
    graph = defaultdict(list)

    for t in tables:
        for fk in t.foreign_keys:
            related_table = fk.foreign_table_name
            graph[related_table].append(t.name)
            in_degree[t.name] += 1

    return in_degree, graph


def sort_tables_by_in_degree(in_degree: dict) -> list[str]:
    """Sort tables based on in-degree values."""
    sorted_tables = sorted(in_degree.keys(), key=lambda x: (in_degree[x], x))
    return sorted_tables


def reorganize_tables_by_relationships(sorted_tables: list[str], relationships: list[RelationshipInfo]) -> list[str]:
    """Reorganize the initial sorted list of tables based on relationships."""
    new_sorted_tables = sorted_tables.copy()
    for relationship in relationships:
        table = relationship.table_name
        foreign_table = relationship.related_table_name
        relation_type = relationship.relation_type

        # Only consider non-many-to-many relationships
        if relation_type != RelationType.MANY_TO_MANY:
            # Get the indexes of the table and foreign table
            table_index = new_sorted_tables.index(table)
            foreign_table_index = new_sorted_tables.index(foreign_table)

            # If the foreign table appears after the dependent table, reorder them
            if foreign_table_index > table_index:
                # Remove the foreign table and insert it after the dependent table
                new_sorted_tables.remove(foreign_table)
                new_sorted_tables.insert(table_index, foreign_table)

    return new_sorted_tables


def separate_tables_list_by_type(tables: list[TableInfo], table_list: list[str]) -> tuple[list[str], list[str]]:
    """Separate tables into base tables and views."""
    base_tables = []
    views = []

    for t in table_list:
        table = next((table for table in tables if table.name == t), None)
        if table is None:
            logger.warning(f'Could not find table {t}')
            continue

        if table.table_type != 'VIEW':
            base_tables.append(t)
        else:
            views.append(t)

    return base_tables, views


def sort_tables_for_insert(tables: list[TableInfo]) -> tuple[list[str], list[str]]:
    """Sort tables based on foreign key relationships for insertion."""
    in_degree, _ = topological_sort(tables)
    initial_sorted_list = sort_tables_by_in_degree(in_degree)
    relationships = [r for t in tables for r in t.relationships]
    sorted_tables = reorganize_tables_by_relationships(initial_sorted_list, relationships)

    return separate_tables_list_by_type(tables, sorted_tables)
