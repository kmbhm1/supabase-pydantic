import pprint
import subprocess
from collections import defaultdict
from random import choice, random
from typing import Any

from supabase_pydantic.util.constants import RelationType
from supabase_pydantic.util.dataclasses import RelationshipInfo, TableInfo
from supabase_pydantic.util.fake import generate_fake_data

pp = pprint.PrettyPrinter(indent=4)


def run_isort(file_path: str) -> None:
    """Run the isort command on the specified file."""
    try:
        # Run the isort command on the specified file
        _ = subprocess.run(['isort', file_path], check=True, capture_output=True, text=True)
        # print(result.stdout)
        # print(f'isort ran successfully: {file_path}')
    except subprocess.CalledProcessError as e:
        print('An error occurred while running isort:')
        print(e.stderr)


def format_with_ruff(file_path: str) -> None:
    """Run the ruff formatter on a specified Python file."""
    try:
        # Run ruff using subprocess.run
        _ = subprocess.run(['ruff', 'format', file_path], check=True, text=True, capture_output=True)
        # print(f'Ruff formatting successful: {file_path}')
        # print(result.stdout)  # Output the stdout of the ruff command
    except subprocess.CalledProcessError as e:
        print('Error during Ruff formatting:')
        print(e.stderr)  # Print any error output from ruff


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
        table = relationship.table_name[1]
        foreign_table = relationship.related_table_name[1]
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
            print(f'Could not find table {t}')
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


def generate_seed_data(tables: list[TableInfo]) -> dict[str, list[list[Any]]]:
    """Generate seed data for the tables."""
    seed_data = {}
    memory: dict[str, dict[str, set[Any]]] = {}
    sorted_tables, _ = sort_tables_for_insert(tables)

    def _remember(table_name: str, column_name: str, data: Any) -> None:
        if table_name not in memory:
            memory[table_name] = dict()
        if column_name not in memory[table_name]:
            memory[table_name][column_name] = set()
        memory[table_name][column_name].add(data)

    for table_name in sorted_tables:
        table = next((t for t in tables if t.name == table_name), None)
        if table is None:
            print(f'Could not find table {table_name}')
            continue

        # Generate fake data for each column
        column_headers = [c.name for c in table.columns]
        fake_data = [column_headers]
        num_rows = random() * 10 + 5
        for _ in range(int(num_rows)):
            row = []
            for column in table.columns:
                # Foreign keys
                if column.is_foreign_key:
                    fk = next((fk for fk in table.foreign_keys if fk.column_name == column.name), None)
                    if fk is None:
                        print(f'Could not find foreign table for column {column.name}')
                        row.append('NULL')
                        continue
                    values = memory[fk.foreign_table_name][fk.foreign_column_name]
                    data = choice(list(values))
                    row.append(data)
                    continue

                # New data
                nullabe = column.is_nullable if column.is_nullable is not None else False
                data = generate_fake_data(column.post_gres_datatype, nullabe, column.max_length, column.name)

                # Unique values
                if column.is_unique:
                    values = memory.get(table_name, {}).get(column.name, set())
                    if len(values) > 0:
                        while data in values:
                            data = generate_fake_data(
                                column.post_gres_datatype, nullabe, column.max_length, column.name
                            )

                # Add to memory
                if not column.is_nullable or column.primary or column.is_unique or column.is_foreign_key:
                    _remember(table_name, column.name, data)

                row.append(data)
            fake_data.append(row)

        # Add foreign keys
        seed_data[table_name] = fake_data

    return seed_data
