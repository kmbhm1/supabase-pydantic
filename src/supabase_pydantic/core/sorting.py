"""Utility functions for sorting tables and dependency management."""

import logging
from collections import defaultdict
from collections.abc import Callable
from itertools import product
from math import inf, prod
from random import choice, randint
from typing import Any

from src.supabase_pydantic.core.constants import RelationType
from src.supabase_pydantic.core.models import RelationshipInfo, TableInfo

MAX_ROWS = 200


def build_dependency_graph(tables: list[TableInfo]) -> tuple[defaultdict[str, list[str]], dict[str, int]]:
    """Build a dependency graph from the tables."""
    graph = defaultdict(list)
    in_degree = {}
    base_tables = [table for table in tables if table.table_type != 'VIEW']  # Exclude views

    # Initialize in_degree for all tables
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

    for table_name in table_list:
        table = next((t for t in tables if t.name == table_name), None)
        if table is None:
            logging.warning(f"Table '{table_name}' not found in table list")
            continue

        if table.table_type == 'VIEW':
            views.append(table_name)
        else:
            base_tables.append(table_name)

    return base_tables, views


def sort_tables_for_insert(tables: list[TableInfo]) -> tuple[list[str], list[str]]:
    """Sort tables based on foreign key relationships for insertion."""
    in_degree, graph = topological_sort(tables)
    sorted_tables = sort_tables_by_in_degree(in_degree)

    # Extract relationships for reorganization
    relationships = []
    for table in tables:
        for fk in table.foreign_keys:
            relationships.append(
                RelationshipInfo(
                    table_name=table.name,
                    related_table_name=fk.foreign_table_name,
                    relation_type=fk.relation_type,
                )
            )

    final_sorted = reorganize_tables_by_relationships(sorted_tables, relationships)
    base_tables, views = separate_tables_list_by_type(tables, final_sorted)

    return base_tables, views


def total_possible_combinations(table: TableInfo) -> float:
    """Get the number of maximum rows for a table based on the unique rows."""
    unique_columns = [col for col in table.columns if col.is_unique or col.primary]

    if not unique_columns:
        return inf

    values_per_column = []
    for col in unique_columns:
        if col.user_defined_values and len(col.user_defined_values) > 0:
            values_per_column.append(len(col.user_defined_values))
        else:
            return inf  # Infinite possibilities for a column without predefined values

    return prod(values_per_column)


def random_num_rows() -> int:
    """Generate a random number of rows."""
    return randint(5, MAX_ROWS)


def pick_random_foreign_key(column_name: str, table: TableInfo, remember_fn: Callable) -> Any:
    """Pick a random foreign key value for a column."""
    # Find the foreign key info for this column
    foreign_key_info = next((fk for fk in table.foreign_keys if fk.column_name == column_name), None)

    if not foreign_key_info:
        logging.warning(f'Foreign key info not found for column {column_name} in table {table.name}')
        return None

    # Get remembered values for the foreign key
    foreign_values = remember_fn(foreign_key_info.foreign_table_name, foreign_key_info.foreign_column_name)

    if not foreign_values:
        logging.warning(
            f'No foreign key values found for {foreign_key_info.foreign_table_name}.{foreign_key_info.foreign_column_name}'
        )
        return None

    # Choose a random value from the foreign values
    return choice(list(foreign_values))


def unique_data_rows(table: TableInfo, remember_fn: Callable) -> list[dict[str, Any]]:
    """Generate unique data rows for a table based on the unique columns."""
    # Get unique columns (either marked as unique or part of a unique constraint)
    unique_columns = [col for col in table.columns if col.is_unique or col.primary]

    # If no unique columns, return empty list (infinite possibilities)
    if not unique_columns:
        return []

    # Calculate maximum number of combinations
    max_combinations = total_possible_combinations(table)

    if max_combinations == inf:
        # For infinite possibilities, generate a random number of rows
        num_rows = random_num_rows()
        rows = []

        for _ in range(num_rows):
            row = {}
            for col in table.columns:
                if col.is_foreign_key:
                    # Use existing foreign key values if available
                    row[col.name] = pick_random_foreign_key(col.name, table, remember_fn)
                elif col.user_defined_values and len(col.user_defined_values) > 0:
                    # Choose a random value from the defined values
                    row[col.name] = choice(col.user_defined_values)
                else:
                    # For columns without predefined values, use None as placeholder
                    # In a real implementation, this would be replaced with generated fake data
                    row[col.name] = None
            rows.append(row)

        return rows

    # For finite possibilities with user-defined values
    # Generate all possible combinations of unique column values
    unique_values = []
    for col in unique_columns:
        if col.user_defined_values and len(col.user_defined_values) > 0:
            unique_values.append((col.name, col.user_defined_values))

    all_combinations = list(product(*[values for _, values in unique_values]))
    rows = []

    # Create rows from these combinations
    for combination in all_combinations:
        row = {}
        for (col_name, _), value in zip(unique_values, combination):
            row[col_name] = value
        rows.append(row)

    return rows
