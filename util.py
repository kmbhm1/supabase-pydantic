import psycopg2
from psycopg2 import sql
import os


def connect_to_database(db_name, user, password, host, port):
    """
    Connects to the PostgreSQL database and returns the connection object.
    """
    try:
        conn = psycopg2.connect(
            dbname=db_name, user=user, password=password, host=host, port=port
        )
        return conn
    except Exception as e:
        print(f"An error occurred while connecting to the database: {e}")
        return None


def get_all_table_names(conn):
    """
    Retrieves all user-defined table names from the database.
    """
    table_names = []
    cur = conn.cursor()
    cur.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    )
    for row in cur.fetchall():
        table_names.append(row[0])
    cur.close()
    return table_names


def get_table_column_details(conn, table_name):
    """
    Retrieves column details for a given table.
    """
    column_details = []
    cur = conn.cursor()
    query = sql.SQL(
        "SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = {}"
    ).format(sql.Literal(table_name))
    cur.execute(query)
    column_details = cur.fetchall()
    cur.close()
    return column_details


def get_table_schema(conn):
    """
    Retrieves schema details for all tables in JSON format.
    """
    schema_details = {}
    tables = get_all_table_names(conn)
    for table in tables:
        columns = get_table_column_details(conn, table)
        schema_details[table] = [
            {"name": col[0], "type": col[1], "max_length": col[2]} for col in columns
        ]
    return schema_details


def postgres_to_pydantic_type(pg_type):
    """
    Maps PostgreSQL column types to Pydantic (Python) types.
    """
    mapping = {
        "integer": "int",
        "text": "str",
        "varchar": "str",
        "timestamp": "datetime",
        # Add more mappings as needed
    }
    return mapping.get(pg_type, "Any")


def generate_pydantic_parent_model(table_name, columns):
    """
    Generates a Pydantic BaseModel class definition for a given table.
    """
    class_definition = f"class {table_name.capitalize()}(BaseModel):\n"
    for column in columns:
        py_type = postgres_to_pydantic_type(column["type"])
        class_definition += f"    {column['name']}: Optional[{py_type}] = None\n"
    return class_definition


def generate_imports_string(column_details):
    """
    Generates a string of necessary imports based on the column types used in the models.
    """
    # Initialize a set to hold unique types to determine necessary imports
    unique_types = set()
    for table_name, columns in column_details.items():
        for column in columns:
            py_type = postgres_to_pydantic_type(column["type"])
            unique_types.add(py_type)

    # Initialize the import string with Pydantic BaseModel import
    imports_str = "from pydantic import BaseModel\n"

    # Add typing imports if necessary
    typing_lib_objects = ["Optional", "Any"]  # Parent objects will always use these
    if "List" in unique_types:
        typing_lib_objects.append("List")

    if len(typing_lib_objects) > 0:
        imports_str += f"from typing import {', '.join(typing_lib_objects)}\n"

    # Check if datetime type is used and add datetime import
    if "datetime" in unique_types:
        imports_str += "from datetime import datetime\n"

    imports_str += "\n"  # Add a newline for readability
    return imports_str


def save_model_to_file(directory, filename, imports_str, all_models_str):
    """
    Saves the generated imports and model string to a file within the specified directory.
    """
    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the full path to the file
    file_path = os.path.join(directory, filename)

    # Delete the file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Write the imports and model string to the file, overwriting if it exists
    with open(file_path, "w") as file:
        file.write(imports_str + "\n" + all_models_str)


def remove_last_two_newlines(s):
    """
    Removes the last two newline characters from a string if they exist.
    """
    # Ensure there are at least two newline characters at the end
    if s.endswith("\n\n"):
        return s[:-2]  # Remove the last two characters
    else:
        return s  # Return the original string if there aren't two newlines at the end
