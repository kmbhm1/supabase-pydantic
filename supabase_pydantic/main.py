# Example usage to generate Pydantic models and save them
import os
import pprint

from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.util import (
    construct_table_info,
    create_connection,
    query_database,
    check_connection,
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_TABLE_COLUMN_DETAILS,
    write_pydantic_model_string,
    run_isort,
    write_sqlalchemy_model_string,
    write_jsonapi_pydantic_model_string,
)
from supabase_pydantic.util.constants import GET_CONSTRAINTS

# Pretty print for testing
pp = pprint.PrettyPrinter(indent=4)

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Replace these variables with your database connection details
db_name = os.environ.get('DB_NAME')
user = os.environ.get('DB_USER')
password = os.environ.get('DB_PASS')
host = os.environ.get('DB_HOST')
port = os.environ.get('DB_PORT')


def check_readiness():
    """Check if environment variables are set correctly."""
    check = {'DB_NAME': db_name, 'DB_USER': user, 'DB_PASS': password, 'DB_HOST': host, 'DB_PORT': port}
    for k, v in check.items():
        # print(k, v)
        if v is None:
            print(f'Environment variables not set correctly. {k} is missing. Please set it in .env file.')
            print('Exiting...')
            return False

    return True


# Main function to execute the whole process
def main():
    # Load environment variables from .env file & check if they are set correctly
    load_dotenv(find_dotenv())
    assert check_readiness()

    default_directory = 'entities'
    jsonapi_directory = os.path.join(default_directory, 'fastapi_jsonapi')
    fastapi_directory = os.path.join(default_directory, 'fastapi')

    try:
        # Create a connection to the database & check if connection is successful
        conn = create_connection(db_name, user, password, host, port)
        assert check_connection(conn)

        # Fetch table column details & foreign key details
        column_details = query_database(conn, GET_ALL_PUBLIC_TABLES_AND_COLUMNS)
        fk_details = query_database(conn, GET_TABLE_COLUMN_DETAILS)
        constraints = query_database(conn, GET_CONSTRAINTS)
        tables = construct_table_info(column_details, fk_details, constraints)
    except Exception as e:
        raise e
    finally:
        if conn:
            conn.close()
            print('Connection closed.')

    # Create Pydantic models
    pydantic_models_string = write_pydantic_model_string(tables)
    pydantic_schemas_path = os.path.join(fastapi_directory, 'schemas.py')

    sql_alchemy_models_string = write_sqlalchemy_model_string(tables)
    sql_alchemy_models_path = os.path.join(jsonapi_directory, 'database.py')

    pydantic_jsonapi_models_string = write_jsonapi_pydantic_model_string(tables)
    pydantic_jsonapi_schemas_path = os.path.join(jsonapi_directory, 'schemas.py')

    content = [pydantic_models_string, sql_alchemy_models_string, pydantic_jsonapi_models_string]
    path = [pydantic_schemas_path, sql_alchemy_models_path, pydantic_jsonapi_schemas_path]

    # Check if the directory exists, if not, create it
    for d in [default_directory, jsonapi_directory, fastapi_directory]:
        if not os.path.exists(d):
            os.makedirs(d)

    # Define the full path to the file
    for s, fp in zip(content, path):
        with open(fp, 'w') as file:
            file.write(s)

        try:
            run_isort(fp)
        except Exception as e:
            print('An error occurred while running isort.')
            print(e)


if __name__ == '__main__':
    main()
