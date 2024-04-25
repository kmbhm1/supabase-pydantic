import builtins
from datetime import date, datetime
import decimal
import json
import keyword
import os
from collections import deque
from random import random, choice

import psycopg2
from faker import Faker

from constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_TABLE_COLUMN_DETAILS,
    ColumnInfo,
    ForeignKeyInfo,
    ModelGenerationType,
    RelationType,
    TableInfo,
    pydantic_type_map,
)

fake = Faker()


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o):  # noqa: D102
        if isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, datetime | date):
            return o.isoformat()
        return super().default(o)


def postgres_to_pydantic_type(column: ColumnInfo):
    """Map PostgreSQL types to Pydantic types."""
    base_type = pydantic_type_map.get(column.post_gres_datatype, ('str', None))[0]

    # Handle optional fields and default values
    if column.is_nullable:
        if column.alias is not None:
            return f'{base_type} | None = Field(default=None, alias="{column.alias}")'
        return f'{base_type} | None = None'
    # elif column.default is not None:
    #     return f"{base_type} = {column.default}"
    else:
        if column.alias is not None:
            return f'{base_type} = Field(alias="{column.alias}")'
        return base_type


def generate_pydantic_parent_name(table_name: str) -> str:
    """Generate the name of the Pydantic parent class."""
    return f'{to_pascal_case(table_name)}Parent'


def generate_pydantic_model(
    table_info: TableInfo,
    all_tables: list[TableInfo],
    model_generation_type: ModelGenerationType = ModelGenerationType.PARENT,
) -> str:
    """Generate Pydantic model class definitions from TableInfo."""
    table_name: str
    lines: list[str]

    is_parent = model_generation_type == ModelGenerationType.PARENT
    parent_table = generate_pydantic_parent_name(table_info.name)
    table_name = parent_table if is_parent else to_pascal_case(table_info.name)
    lines = [
        f'class {table_name}({"BaseModel" if is_parent else parent_table}):'  # noqa: E501
    ]
    sort_for_parent = True if is_parent else False
    table_info.columns = table_info.sort_and_combine_columns_for_pydantic_model(sort_for_parent)

    for column in table_info.columns:
        if is_parent:
            base_type = pydantic_type_map.get(column.post_gres_datatype, ('str', None))[0]
            if column.alias is not None:
                pydantic_type = f'{base_type} | None = Field(default=None, alias="{column.alias}")'
            else:
                pydantic_type = f'{base_type} | None = None'
        else:
            pydantic_type = postgres_to_pydantic_type(column)
        lines.append(f'    {column.name}: {pydantic_type}')

    # Generate related model fields based on ForeignKeyInfo
    if model_generation_type == ModelGenerationType.MAIN:
        if len(table_info.foreign_keys) > 0:
            lines.append('\n    # Foreign key fields')
        for fk in table_info.foreign_keys:
            related_table = next((t for t in all_tables if t.name == fk.foreign_table_name), None)
            if related_table:
                related_field = f'{fk.column_name}_{related_table.name.lower()}'
                # relation_type = 'List' if fk.relation_type == RelationType.ONE_TO_MANY else related_table.name.capitalize()
                relation_type = f'list[{generate_pydantic_parent_name(related_table.name)}] | {generate_pydantic_parent_name(related_table.name)}'  # noqa: E501
                lines.append(f'    {related_field}: {relation_type} | None = []')

    return '\n'.join(lines)


def generate_all_pydantic_models(tables: list[TableInfo]):
    parent_models = [generate_pydantic_model(table, tables, ModelGenerationType.PARENT) for table in tables]
    parent_imports = generate_imports_for_pydantic_models(tables, ModelGenerationType.PARENT, None)
    parent_model_str = parent_imports + '\n' + '\n\n\n'.join(parent_models)

    main_models = [generate_pydantic_model(table, tables, ModelGenerationType.MAIN) for table in tables]
    parent_model_names = [generate_pydantic_parent_name(table.name) for table in tables]
    main_imports = generate_imports_for_pydantic_models(tables, ModelGenerationType.MAIN, parent_model_names)
    main_model_str = main_imports + '\n' + '\n\n\n'.join(main_models)

    return {'parents.py': parent_model_str, 'models.py': main_model_str}


def get_pydantic_type(data_type: str):
    return pydantic_type_map.get(data_type, ('Any', 'from typing import Any'))


def consolidate_imports(import_list):
    from_imports = {}

    # Parsing and aggregating imports
    for imp in import_list:
        parts = imp.split()
        if 'from' in imp:
            module = parts[1]
            import_part = imp.split('import')[1].strip()
            if module not in from_imports:
                from_imports[module] = []
            from_imports[module].append(import_part)
        elif 'import' in imp:
            # Direct 'import module' handling, assuming they are single and already consolidated
            module = parts[1]
            if module not in from_imports:
                from_imports[module] = []

    # Constructing consolidated import statements
    consolidated_imports = []
    for module, imports in from_imports.items():
        if imports:
            # Combine imports for 'from' type statements
            import_string = ', '.join(sorted(set(imports)))
            consolidated_imports.append(f'from {module} import {import_string}')
        else:
            # Direct import, just append
            consolidated_imports.append(f'import {module}')

    return consolidated_imports


def sort_imports(import_list: list[str]):
    # Categories
    standard_libs = []
    third_party_libs = []
    local_libs = []

    import_list = consolidate_imports(import_list)

    # Categorizing imports (this example assumes the user categorizes them manually)
    for imp in import_list:
        if 'import' in imp and '.' not in imp.split()[1]:
            standard_libs.append(imp)
        elif 'from' in imp:
            local_libs.append(imp)
        else:
            third_party_libs.append(imp)

    # Sorting each category
    standard_libs.sort()
    third_party_libs.sort()
    local_libs.sort()

    # Combine all imports into a single list with proper newlines
    sorted_imports = '\n\n'.join(standard_libs + third_party_libs + local_libs)
    return sorted_imports


def get_parent_model_import_string(parent_models: list[str] | None):
    candidate_line = ', '.join(parent_models) if parent_models is not None else '*'
    if len(candidate_line) > 88:
        x = ',\n    '.join(parent_models or ['*'])
        return 'from .parents import (\n    ' + x + '\n)'
    return f'from .parents import {candidate_line}'


def generate_imports_for_pydantic_models(
    tables: list[TableInfo],
    model_generation_type: ModelGenerationType = ModelGenerationType.PARENT,
    parent_models: list[str] | None = None,
):
    imports: set[str] = set()
    unique_types: set[str] = set()
    is_parent = model_generation_type == ModelGenerationType.PARENT

    parent_import_string = get_parent_model_import_string(parent_models)
    final_import = 'from pydantic import BaseModel' if is_parent else parent_import_string
    imports.add(final_import)

    has_alias = any(bool(c.alias is not None) for t in tables for c in t.columns)
    if has_alias:
        imports.add('from pydantic import Field')

    for table in tables:
        for column in table.columns:
            pydantic_type, import_statement = get_pydantic_type(column.post_gres_datatype)
            if import_statement:
                imports.add(import_statement)
            unique_types.add(pydantic_type)

    return sort_imports(list(imports)) + '\n\n'


def save_model_to_file(directory, filename, imports_str, all_models_str):
    """Saves the generated imports and model string to a file within the specified directory."""
    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the full path to the file
    file_path = os.path.join(directory, filename)

    # Delete the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write the imports and model string to the file, overwriting if it exists
    with open(file_path, 'w') as file:
        file.write(imports_str + '\n' + all_models_str)


def to_pascal_case(string):
    """Converts a string to PascalCase."""
    words = string.split('_')
    camel_case = ''.join(word.capitalize() for word in words)
    return camel_case


# Function to create a database connection
def create_connection(dbname, user, password, host, port):
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn


# Function to fetch all public table column details
def fetch_table_column_details(conn):
    cur = conn.cursor()
    cur.execute(GET_ALL_PUBLIC_TABLES_AND_COLUMNS)
    column_details = cur.fetchall()
    cur.close()
    return column_details


# Function to fetch foreign key details
def fetch_foreign_key_details(conn):
    cur = conn.cursor()
    cur.execute(GET_TABLE_COLUMN_DETAILS)
    fk_details = cur.fetchall()
    cur.close()
    return fk_details


def check_and_replace_column_name(column_name: str) -> tuple[str, str | None]:
    """Check if the column name is valid.

    The column name is invalid if it is a Python built-in name or prepended with "model_".
    This function changes the columne name to "field_{column_name}" if it is invalid and
    returns the original column name as an alias for Pydantic.

    Parameters:
        column_name (str): The original name of the column.

    Returns:
        tuple: A tuple containing the potentially modified column name and the Pydantic alias if applicable.
    """

    # Check if the name is a built-in or keyword or starts with "model_"
    if column_name in dir(builtins) or column_name in keyword.kwlist or column_name.startswith('model_'):
        # Rename the column to avoid conflict
        new_column_name = f'field_{column_name}'
        # Provide the original column name as an alias for Pydantic
        return new_column_name, column_name
    else:
        # No conflict, return the original name and None for alias
        return column_name, None


# Function to construct TableInfo objects
def construct_table_info(column_details, fk_details):
    tables = {}

    # Process columns
    for row in column_details:
        schema, table_name, column_name, default, is_nullable, data_type, max_length = row
        table_key = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema)
        valid_column_name, alias = check_and_replace_column_name(column_name)
        column_info = ColumnInfo(
            name=valid_column_name,
            alias=alias,
            post_gres_datatype=data_type,
            datatype=pydantic_type_map.get(data_type, ('Any, from typing import Any'))[0],
            default=default,
            is_nullable=is_nullable == 'YES',
            max_length=max_length,
        )
        tables[table_key].add_column(column_info)

    # Process foreign keys
    for row in fk_details:
        (
            table_schema,
            table_name,
            column_name,
            foreign_table_schema,
            foreign_table_name,
            foreign_column_name,
            constraint_name,
        ) = row
        table_key = (table_schema, table_name)
        valid_column_name, _ = check_and_replace_column_name(column_name)
        if table_key in tables:
            fk_info = ForeignKeyInfo(
                constraint_name=constraint_name,
                column_name=valid_column_name,
                foreign_table_name=foreign_table_name,
                foreign_column_name=foreign_column_name,
                relation_type=RelationType.ONE_TO_MANY,  # Simplified assumption
                foreign_table_schema=foreign_table_schema,
            )
            tables[table_key].add_foreign_key(fk_info)

    return list(tables.values())


def get_table_dependencies(tables: list[TableInfo]):
    """Get the dependencies of each table."""
    dependencies = {}
    for table in tables:
        # Each table's dependencies are the tables it has a foreign key reference to
        dependencies[table.name] = {fk.foreign_table_name for fk in table.foreign_keys}
    return dependencies


def topological_sort(dependencies: dict) -> list:
    """Perform topological sorting on the dependencies."""
    # Step 1: Identify all items with no dependencies
    in_degree = {item: 0 for item in dependencies}
    for deps in dependencies.values():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1
            else:
                in_degree[dep] = 1

    # Use a queue to keep all items with no incoming dependency
    queue = deque([item for item in in_degree if in_degree[item] == 0])
    sorted_order = []

    while queue:
        item = queue.popleft()
        sorted_order.append(item)
        # Reduce the in-degree of dependent items
        for dependent in dependencies.get(item, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(sorted_order) == len(in_degree):  # Check for cycle
        return sorted_order
    else:
        raise Exception('There is a cycle in the dependencies which prevents topological sorting.')


def generate_data_in_order(tables: list[TableInfo]):
    dependencies = get_table_dependencies(tables)
    sorted_table_names = topological_sort(dependencies)
    return sorted_table_names


def generate_fake_data(column: ColumnInfo, fake: Faker = Faker()):
    datatype = column.post_gres_datatype.lower()

    if column.is_nullable and random() < 0.15:
        return 'NULL'

    if datatype in ['integer', 'bigint']:
        return fake.random_number(digits=column.max_length if column.max_length else 5)
    elif datatype == 'text' or 'varchar' in datatype or datatype == 'character varying':
        if column.name.lower() == 'email':
            return f"'{fake.email()}'"
        return f"'{fake.text(max_nb_chars=column.max_length if column.max_length else 20)}'"
    elif datatype == 'boolean':
        return fake.boolean()
    elif datatype == 'date':
        return f"'{fake.date()}'"
    elif datatype == 'timestamp':
        return f"'{fake.date_time()}'"
    elif datatype == 'timestamp with time zone':
        return f"'{fake.date_time()}'"
    elif datatype == 'timestamp without time zone':
        return f"'{fake.date_time()}'"
    elif datatype == 'uuid':
        return f"'{fake.uuid4()}'"
    elif datatype in ['json', 'jsonb']:
        return f"'{json.dumps(fake.profile(), cls=CustomJsonEncoder)}'"
    else:
        return 'NULL'


def reset_all_generated_data(tables: list[TableInfo]):
    for table in tables:
        table.generated_data = []


def create_insert_statements(tables: list[TableInfo], num_entries: int = 50):
    ordered_table_names = generate_data_in_order(tables)
    table_map = {table.name: table for table in tables}
    sql_statements = []

    for table_name in ordered_table_names:
        table = table_map[table_name]
        for _ in range(num_entries):
            column_names = []
            column_values = []

            row_data = {}
            for col in table.columns:
                fk = next((fk for fk in table.foreign_keys if fk.column_name == col.name), None)
                if fk:
                    # If it's a foreign key, pull a random value from the related table's generated data
                    related_table = table_map[fk.foreign_table_name]
                    if related_table.generated_data:
                        related_value = choice(related_table.generated_data)[fk.foreign_column_name]
                        row_data[col.name] = related_value
                        column_values.append(str(related_value))
                else:
                    # Generate fake data normally
                    value = generate_fake_data(col)
                    row_data[col.name] = value
                    column_values.append(value)

                column_names.append(col.name)

            table.generated_data.append(row_data)  # Store the generated row data
            sql = (
                f"INSERT INTO {table.schema}.{table.name} "
                f"({', '.join(column_names)}) "
                f"VALUES ({', '.join([str(c) for c in column_values])});"
            )
            sql_statements.append(sql)

    return sql_statements
