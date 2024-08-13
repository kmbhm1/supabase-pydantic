import pprint
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
import psycopg2

pp = pprint.PrettyPrinter(indent=4)


# Step 1: Connect to the PostgreSQL database
def connect_to_db(db_name, user, password, host='localhost', port=5432):
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)
    return conn


# Step 2: Fetch the table schema and relationships
def get_table_schema(conn):
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("""
    SELECT table_name, table_type
    FROM information_schema.tables
    WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()

    schema = {}
    relationships = []

    for table in tables:
        table_name = table[0]
        table_type = table[1]

        # Get columns
        cursor.execute(f"""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = '{table_name}'
        """)
        columns = cursor.fetchall()

        # Get foreign keys
        cursor.execute(f"""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table_name}';
        """)
        foreign_keys = cursor.fetchall()

        schema[table_name] = {'table_type': table_type, 'columns': columns, 'foreign_keys': foreign_keys}

        # Identify relationships
        for fk in foreign_keys:
            related_table = fk[1]
            relationships.append((table_name, related_table))

    return schema, relationships


# Step 3: Determine relationship types
def analyze_relationships(schema, relationships):
    relationship_types = []

    for relationship in relationships:
        table, related_table = relationship
        fk_columns = [fk for fk in schema[table]['foreign_keys'] if fk[1] == related_table]
        print(fk_columns)
        if len(fk_columns) == 1:
            # One-to-Many or One-to-One
            related_table_columns = [col[0] for col in schema[related_table]['columns']]
            print(related_table_columns)
            if fk_columns[0][2] in related_table_columns:
                relationship_type = 'One-to-One'
            else:
                relationship_type = 'One-to-Many'
        else:
            # Many-to-Many
            relationship_type = 'Many-to-Many'

        relationship_types.append((table, related_table, relationship_type))

    return relationship_types


# Step 4: Visualize relationships
def visualize_relationships(relationship_types, schema):
    G = nx.DiGraph()

    for table, related_table, relationship_type in relationship_types:
        G.add_edge(table, related_table, label=relationship_type)

    relationship_tables = [i[0] for i in relationship_types]
    for table in schema:
        if table not in relationship_tables:
            if schema[table]['table_type'] != 'VIEW':
                G.add_node(table)
            # else:
            #     G.add_node(table, color='purple')

    pos = nx.circular_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color='lightblue',
        font_size=8,
        font_weight='regular',
    )

    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title('Database Table Relationships')
    # plt.show()

    plt.savefig('./poc/database_relationships.png')


def identify_top_level_tables(schema):
    # Initialize a dictionary to track which tables are referenced by others
    referenced_tables = defaultdict(int)

    for table in schema:
        for fk in schema[table]['foreign_keys']:
            related_table = fk[1]
            referenced_tables[related_table] += 1

    # Tables not referenced by any other tables are top-level
    top_level_tables = [table for table in schema if referenced_tables[table] == 0]

    return top_level_tables


def build_graph(relationships):
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_tables = set()

    for table_a, table_b, _ in relationships:
        graph[table_a].append(table_b)
        in_degree[table_b] += 1
        all_tables.update([table_a, table_b])

    return graph, in_degree, all_tables


def dfs(node, graph, visited, component):
    stack = [node]
    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            component.append(current)
            for neighbor in graph[current]:
                if neighbor not in visited:
                    stack.append(neighbor)


def find_separated_networks(graph, all_tables):
    visited = set()
    networks = []

    for table in all_tables:
        if table not in visited:
            component = []
            dfs(table, graph, visited, component)
            networks.append(component)

    return networks


# needed


def initial_sorted_tables(in_degree):
    """Create an initial sorted list of tables based on in-degree values.

    If tables have the same in-degree, sort them alphabetically.

    Args:
        in_degree (dict): A dictionary containing the in-degree values of each table.

    """
    # Sort the tables by in-degree first, then alphabetically)
    sorted_tables = sorted(in_degree.keys(), key=lambda x: (in_degree[x], x))
    return sorted_tables


def reorganize_tables_by_relationships(sorted_tables, relationships) -> list[str]:
    """Reorganize the initial sorted list of tables.

    This action is based on the relationships to ensure foreign key dependencies are respected.

    Args:
        sorted_tables (list): A list of tables sorted by in-degree and then alphabetically.
        relationships (list): A list of relationships between tables.
    """
    for relationship in relationships:
        table, foreign_table, relationship_type = relationship

        # Only consider non-many-to-many relationships
        if relationship_type != 'Many-to-Many':
            # Get the indexes of the table and foreign table
            table_index = sorted_tables.index(table)
            foreign_table_index = sorted_tables.index(foreign_table)

            # If the foreign table appears after the dependent table, reorder them
            if foreign_table_index > table_index:
                # Remove the foreign table and insert it after the dependent table
                sorted_tables.remove(foreign_table)
                sorted_tables.insert(table_index, foreign_table)

    return sorted_tables


def topological_sort(schema):
    """Perform a topological sort on the tables based on their foreign key dependencies."""
    # Use Kahn's algorithm for topological sorting
    in_degree = {table: 0 for table in schema}
    graph = defaultdict(list)

    for table in schema:
        for fk in schema[table]['foreign_keys']:
            related_table = fk[1]
            graph[related_table].append(table)
            in_degree[table] += 1

    return in_degree, graph


def sort_for_inserts(schema, relationships):
    """Sort the tables based on their relationships and foreign key dependencies."""
    in_degree, _ = topological_sort(schema)
    sorted_tables_by_in_degree = initial_sorted_tables(in_degree)
    s = reorganize_tables_by_relationships(sorted_tables_by_in_degree, relationships)
    views, tables = (
        [x for x in s if schema[x]['table_type'] == 'VIEW'],
        [x for x in s if schema[x]['table_type'] != 'VIEW'],
    )

    return tables, views


# Main Function
if __name__ == '__main__':
    # Specify your PostgreSQL database credentials
    db_name = 'postgres'
    user = 'postgres'
    password = 'postgres'
    host = 'localhost'  # or your PostgreSQL host
    port = 54322  # default PostgreSQL port

    conn = connect_to_db(db_name, user, password, host, port)
    schema, relationships = get_table_schema(conn)
    relationship_types = analyze_relationships(schema, relationships)
    tables, views = sort_for_inserts(schema, relationship_types)

    pp.pprint(
        {
            'Relationships': relationship_types,
            'Sorted Tables': tables,
            'Views': views,
        }
    )

    visualize_relationships(relationship_types, schema)
