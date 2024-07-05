import subprocess
from collections import defaultdict, deque
from supabase_pydantic.util.constants import CUSTOM_MODEL_NAME, CUSTOM_JSONAPI_META_MODEL_NAME
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


# Pydantic


def write_custom_model_string() -> str:
    """Generate a custom Pydantic model."""
    return '\n'.join([f'class {CUSTOM_MODEL_NAME}(BaseModel):', '\tpass'])


def write_pydantic_imports_string(tables: list[TableInfo]) -> str:
    """Generate the import statements for the Pydantic models."""
    imports_set = set()
    for t in tables:
        _, i = t.get_pydantic_imports()
        imports_set.update(i)

    return '\n'.join(sorted(imports_set))


def write_forward_refs_string(tables: list[TableInfo], is_base: bool = False) -> str:
    """Generate the forward references for the Pydantic models."""
    forward_refs = set()
    for table in tables:
        forward_refs.update(table.table_forward_refs(is_base))

    return '\n'.join(sorted(forward_refs))


def write_pydantic_model_string(tables: list[TableInfo]) -> str:
    """Generate the Pydantic model strings for all tables."""
    # imports
    imports_string = write_pydantic_imports_string(tables)

    # custom model
    custom_model_section_comment = (
        '#' * 30
        + ' Custom Model Class'
        + '\n# Note: This is a custom model class for defining common features amongst Base Schema.'
    )
    custom_model_string = write_custom_model_string()

    # forward refs
    # note: forward refs mitigate for circular imports and cases where referenced types
    # are not yet defined in the current module, when writing.
    # forward_refs_section_comment = (
    #     '#' * 30
    #     + ' Forward References'
    #     + '\n# Note: Forward references are used to mitigate circular importing.'
    #     + '\n# See Python docs at https://docs.python.org/3/library/typing.html#typing.ForwardRef'
    #     + '\n# and https://docs.pydantic.dev/2.8/concepts/postponed_annotations/ for more information.'
    # )
    # forward_refs_string = write_forward_refs_string(tables, True)

    # parent classes
    base_section_comment = '#' * 30 + ' Base Classes'
    base_string = '\n\n\n'.join([table.write_pydantic_base_class() for table in tables])

    # working classes
    working_section_comment = '#' * 30 + ' Working Classes'
    working_string = '\n\n\n'.join([table.write_pydantic_working_class() for table in tables])

    return (
        '\n\n\n'.join(
            [
                imports_string,
                custom_model_section_comment,
                custom_model_string,
                base_section_comment,
                base_string,
                working_section_comment,
                working_string,
            ]
        )
        + '\n\n\n'
    )


# Sqlalchemy


def write_declarative_base_string() -> str:
    """Generate the declarative base string for SQLAlchemy."""
    return 'Base = declarative_base()'


def write_sqlalchemy_imports_string(tables: list[TableInfo]) -> str:
    """Generate the import statements for the SQLAlchemy models."""
    imports_set = set()
    for t in tables:
        _, i = t.get_sqlalchemy_imports()
        imports_set.update(i)

    return '\n'.join(sorted(imports_set))


def write_sqlalchemy_model_string(tables: list[TableInfo]) -> str:
    """Generate the SQLAlchemy model strings for all tables."""
    # imports
    imports_string = write_sqlalchemy_imports_string(tables)

    # declarative base
    declarative_base_section_comment = '#' * 30 + ' Declarative Base'
    declarative_base_string = write_declarative_base_string()

    # classes
    classes_section_comment = '#' * 30 + ' Classes'
    classes_string = '\n\n\n'.join([table.write_sqlalchemy_class() for table in tables])

    return (
        '\n\n\n'.join(
            [
                imports_string,
                declarative_base_section_comment,
                declarative_base_string,
                classes_section_comment,
                classes_string,
            ]
        )
        + '\n\n\n'
    )


# FastAPI-JSONAPI


def write_jsonapi_pydantic_meta_model_string() -> str:
    """Generate a custom Pydantic model."""
    return '\n'.join([f'class {CUSTOM_MODEL_NAME}({CUSTOM_JSONAPI_META_MODEL_NAME}):', '\tpass'])


def write_jsonapi_pydantic_imports_string(tables: list[TableInfo]) -> str:
    """Generate the import statements for the Pydantic models."""
    imports_set = set()
    for t in tables:
        _, i = t.get_fastapi_jsonapi_pydantic_imports()
        imports_set.update(i)

    return '\n'.join(sorted(imports_set))


def write_jsonapi_pydantic_model_string(tables: list[TableInfo]) -> str:
    """Generate the Pydantic model strings for all tables."""
    # imports
    imports_string = write_jsonapi_pydantic_imports_string(tables)

    # custom model
    custom_model_section_comment = (
        '#' * 30
        + ' Custom Model Class'
        + '\n# Note: This is a custom model class for defining common features amongst Base Schema.'
    )
    custom_model_string = write_jsonapi_pydantic_meta_model_string()

    # base classes
    base_section_comment = '#' * 30 + ' Base Classes'
    base_string = '\n\n'.join([table.write_jsonapi_pydantic_base_class('BaseModel') for table in tables])

    # working classes
    working_section_comment = '#' * 30 + ' Working Classes'
    working_string = '\n\n\n'.join(
        [f'# {table.name}' + table.write_jsonapi_pydantic_working_class() for table in tables]
    )

    return (
        '\n\n\n'.join(
            [
                imports_string,
                custom_model_section_comment,
                custom_model_string,
                base_section_comment,
                base_string,
                working_section_comment,
                working_string,
            ]
        )
        + '\n\n\n'
    )
