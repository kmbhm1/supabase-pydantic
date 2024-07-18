import os
import pprint
import shutil

from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.util import (
    construct_table_info,
    create_connection,
    query_database,
    check_connection,
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_CONSTRAINTS,
    GET_TABLE_COLUMN_DETAILS,
    run_isort,
    FrameworkType,
    FileWriter,
    OrmType,
    WriterConfig,
)
import click

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


def reload_env() -> tuple:
    # Load environment variables from .env file
    load_dotenv(find_dotenv())

    # Replace these variables with your database connection details
    db_name = os.environ.get('DB_NAME')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASS')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')

    return db_name, user, password, host, port


def check_readiness():
    """Check if environment variables are set correctly."""
    # db_name, user, password, host, port = reload_env()
    check = {'DB_NAME': db_name, 'DB_USER': user, 'DB_PASS': password, 'DB_HOST': host, 'DB_PORT': port}
    for k, v in check.items():
        # print(k, v)
        if v is None:
            print(f'Environment variables not set correctly. {k} is missing. Please set it in .env file.')
            print('Exiting...')
            return False

    return True


def clean_directory(directory: str):
    """Remove all files & directories in the specified directory."""
    if os.path.isdir(directory) and not os.listdir(directory):
        os.rmdir(directory)
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'An error occurred while deleting {file_path}.')
                print(e)


def clean_directories(directories: list):
    """Remove all files & directories in the specified directories."""
    for d in directories:
        print(f'Checking for directory: {d}')
        if not os.path.isdir(d):
            print(f'Directory {d} does not exist.')
            return

        print(f'Cleaning directory: {d}')
        clean_directory(d)


def generate_unique_filename(base_name: str, extension: str, directory: str = '.') -> str:
    """Generate a unique filename based on the base name & extension.

    Args:
        base_name (str): The base name of the file (without extension)
        extension (str): The extension of the file (e.g., 'py', 'json', 'txt')
        directory (str): The directory where the file will be saved

    Returns:
        str: The unique file name

    """
    extension = extension.lstrip('.')
    file_name = f'{base_name}.{extension}'
    file_path = os.path.join(directory, file_name)
    i = 1
    while os.path.exists(file_path):
        file_name = f'{base_name}_{i}.{extension}'
        file_path = os.path.join(directory, file_name)
        i += 1

    print(file_path)
    return file_path


@click.command()
@click.option(
    '-d', '--directory', 'default_directory', default='entities', help='The directory to save the generated files.'
)
@click.option('-a', '--all', '_all', is_flag=True, help='Generate all model files. Overrides other flags.')
@click.option('--overwrite/--no-overwrite', default=True, help='Overwrite existing files.')
@click.option(
    '--sqlalchemy', 'generate_sqlalchemy', is_flag=True, help='Add SQLAlchemy database models to the generated files.'
)
@click.option('--fastapi-jsonapi', 'generate_jsonapi', is_flag=True, help='Generate files for FastAPI-JSONAPI.')
@click.option('--nullify-base-schema', is_flag=True, help='Force all default values in Base schema to be nullable.')
@click.option('-c', '--clean', 'cleanup', is_flag=True, help='Remove & clean the generated directory and files.')
def main(
    default_directory: str,
    _all: bool,
    overwrite: bool,
    generate_sqlalchemy: bool,
    generate_jsonapi: bool,
    nullify_base_schema: bool,
    cleanup: bool,
):
    """A CLI tool to generate Pydantic models from a PostgreSQL database."""

    # Load environment variables from .env file & check if they are set correctly
    load_dotenv(find_dotenv())
    assert check_readiness()

    # Check if _all is set to True, if so, set generate_sqlalchemy & generate_jsonapi to True
    if _all:
        generate_sqlalchemy = True
        generate_jsonapi = True

    # Set the default directory & create the directories
    fastapi_directory = os.path.join(default_directory, 'fastapi')
    jsonapi_directory = os.path.join(default_directory, 'fastapi_jsonapi')  # TODO: add later

    directories = [default_directory, fastapi_directory]
    if generate_jsonapi or cleanup:
        directories.append(jsonapi_directory)

    # Clean the directories if the cleanup flag is set
    if cleanup:
        clean_directories(directories)
        return

    # Get Table & Column details from the database
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

    # Check if the directory exists, if not, create it
    for d in directories:
        if not os.path.exists(d):
            os.makedirs(d)

    # Configure the writer jobs
    pydantic_fname, sqlalchemy_fname = 'schemas.py', 'database.py'
    jobs: dict[str, WriterConfig] = {
        'FastAPI Pydantic': WriterConfig(
            file_type=OrmType.PYDANTIC,
            framework_type=FrameworkType.FASTAPI,
            filename=pydantic_fname,
            directory=fastapi_directory,
            enabled=True,
        ),
        'FastAPI SQLAlchemy': WriterConfig(
            file_type=OrmType.SQLALCHEMY,
            framework_type=FrameworkType.FASTAPI,
            filename=sqlalchemy_fname,
            directory=fastapi_directory,
            enabled=generate_sqlalchemy,
        ),
        'FastAPI-JSONAPI Pydantic': WriterConfig(
            file_type=OrmType.PYDANTIC,
            framework_type=FrameworkType.FASTAPI_JSONAPI,
            filename=pydantic_fname,
            directory=jsonapi_directory,
            enabled=generate_jsonapi,
        ),
        'FastAPI-JSONAPI SQLAlchemy': WriterConfig(
            file_type=OrmType.SQLALCHEMY,
            framework_type=FrameworkType.FASTAPI_JSONAPI,
            filename=sqlalchemy_fname,
            directory=jsonapi_directory,
            enabled=generate_jsonapi and generate_sqlalchemy,
        ),
    }

    paths = []
    for job, c in jobs.items():  # c = config
        if not c.enabled:
            continue

        print(f'Generating {job} models...')
        writer = FileWriter(
            tables,
            file_type=c.file_type,
            framework_type=c.framework_type,
            nullify_base_schema_class=nullify_base_schema,
        )
        fpath = generate_unique_filename(c.name(), c.ext(), c.directory) if not overwrite else c.fpath()
        writer.write(fpath)
        paths.append(fpath)
        print(f'{job} models generated successfully: {fpath}')

    try:
        for p in paths:
            run_isort(p)
    except Exception as e:
        print('An error occurred while running isort.')
        print(e)


if __name__ == '__main__':
    main()
