import subprocess
from collections import defaultdict, deque

from supabase_pydantic.util.dataclasses import TableInfo


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


def get_graph_from_tables(tables: list[TableInfo]) -> tuple[defaultdict, dict]:
    """Generate a graph and indegree dictionary from the tables."""
    graph = defaultdict(list)
    indegree = {table.name: 0 for table in tables}

    for table in tables:
        for fk in table.foreign_keys:
            # table.name should point to fk.foreign_table_name
            graph[fk.foreign_table_name].append(table.name)
            indegree[table.name] += 1

    return graph, indegree


def topological_sort(tables: list[TableInfo]) -> list[TableInfo]:
    """Topologically sort the tables based on foreign key relationships."""
    graph, indegree = get_graph_from_tables(tables)
    queue = deque([table.name for table in tables if indegree[table.name] == 0])
    sorted_tables = []

    while queue:
        current = queue.popleft()
        sorted_tables.append(current)

        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_tables) != len(tables):
        print(f'Debug: Graph {graph}')
        print(f'Debug: Indegree {indegree}')
        raise ValueError(f'Cycle detected in the graph. Cannot sort tables. Final list: {sorted_tables}')

    name_to_table = {table.name: table for table in tables}
    return [name_to_table[name] for name in sorted_tables]
