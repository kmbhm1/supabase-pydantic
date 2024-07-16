import subprocess
from collections import defaultdict, deque
from supabase_pydantic.util.dataclasses import TableInfo


def run_isort(file_path: str):
    try:
        # Run the isort command on the specified file
        result = subprocess.run(['isort', file_path], check=True, capture_output=True, text=True)
        print(result.stdout)
        print('isort ran successfully.')
    except subprocess.CalledProcessError as e:
        print('An error occurred while running isort:')
        print(e.stderr)


def get_graph_from_tables(tables: list[TableInfo]) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Generate a graph & indegree dictionary from the tables."""
    graph = defaultdict(list)
    indegree = {table.name: 0 for table in tables}

    for table in tables:
        for fk in table.foreign_keys:
            graph[table.name].append(fk.foreign_table_name)
            indegree[table.name] += 1

    return graph, indegree


def topological_sort(tables: list[TableInfo]) -> list[TableInfo]:
    """Topologically sort the tables based on foreign key relationships."""
    # Build the graph
    graph, indegree = get_graph_from_tables(tables)

    # Find all nodes with no incoming edges
    queue = deque([table.name for table in tables if indegree[table.name] == 0])
    sorted_tables = []

    # Process the graph
    while queue:
        current = queue.popleft()
        sorted_tables.append(current)

        for neighbor in graph[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_tables) != len(tables):
        raise ValueError(f'Cycle detected in the graph. Cannot sort tables. Final list: {sorted_tables}')

    # Convert names back to TableInfo instances
    name_to_table = {table.name: table for table in tables}
    return [name_to_table[name] for name in sorted_tables]
