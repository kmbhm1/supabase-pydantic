import os
from collections.abc import Callable

import psycopg2

from constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_TABLE_COLUMN_DETAILS,
    ColumnInfo,
    ForeignKeyInfo,
    RelationType,
    TableInfo,
    pydantic_type_map,
)


def postgres_to_pydantic_type(column: ColumnInfo):
    """Map PostgreSQL types to Pydantic types."""
    base_type = pydantic_type_map.get(column.post_gres_datatype, ('str', None))[0]

    # Handle optional fields and default values
    if column.is_nullable:
        return f'{base_type} | None = None'
    # elif column.default is not None:
    #     return f"{base_type} = {column.default}"
    else:
        return base_type


def generate_pydantic_parent_name(table_name: str) -> str:
    """Generate the name of the Pydantic parent class."""
    return f'{to_pascal_case(table_name)}Parent'


def generate_pydantic_model(table_info: TableInfo, table_name_fn: Callable | None = None) -> str:
    """Generate Pydantic model class definitions from TableInfo."""
    table_name = table_name_fn(table_info.name) if table_name_fn is not None else table_info.name.capitalize()
    lines = [f'class {table_name}(BaseModel):']
    table_info.columns = table_info.sort_and_combine_columns_for_pydantic_model()
    for column in table_info.columns:
        pydantic_type = postgres_to_pydantic_type(column)
        lines.append(f'    {column.name}: {pydantic_type}')

    return '\n'.join(lines)


def generate_all_pydantic_models(tables: list[TableInfo]):
    parent_models = [generate_pydantic_model(table, generate_pydantic_parent_name) for table in tables]
    return '\n\n'.join(parent_models)


def get_pydantic_type(data_type: str):
    return pydantic_type_map.get(data_type, ('Any', 'from typing import Any'))


def generate_imports_for_pydantic_models(tables: list[TableInfo]):
    imports_needed: set[str] = set()
    unique_types: set[str] = set()

    for table in tables:
        for column in table.columns:
            pydantic_type, import_statement = get_pydantic_type(column.post_gres_datatype)
            if import_statement:
                imports_needed.add(import_statement)
            unique_types.add(pydantic_type)

    # Always import BaseModel from Pydantic
    imports = ['from pydantic import BaseModel']
    imports.extend(sorted(imports_needed))  # Add additional imports sorted for aesthetics
    return '\n'.join(imports) + '\n'


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


# Function to construct TableInfo objects
def construct_table_info(column_details, fk_details):
    tables = {}

    # Process columns
    for row in column_details:
        schema, table_name, column_name, default, is_nullable, data_type, max_length = row
        table_key = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema)
        column_info = ColumnInfo(
            name=column_name,
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
        if table_key in tables:
            fk_info = ForeignKeyInfo(
                constraint_name=constraint_name,
                column_name=column_name,
                foreign_table_name=foreign_table_name,
                foreign_column_name=foreign_column_name,
                relation_type=RelationType.ONE_TO_MANY,  # Simplified assumption
                foreign_table_schema=foreign_table_schema,
            )
            tables[table_key].add_foreign_key(fk_info)

    return list(tables.values())
