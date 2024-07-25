import os
import pprint
from typing import Any

import click
import toml
from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.util import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_CONSTRAINTS,
    GET_TABLE_COLUMN_DETAILS,
    FileWriterFactory,
    FrameWorkType,
    OrmType,
    WriterConfig,
    check_connection,
    clean_directories,
    construct_table_info,
    create_connection,
    format_with_ruff,
    query_database,
    run_isort,
)
from supabase_pydantic.util.dataclasses import AppConfig, ToolConfig

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
    """Reload environment variables from .env file."""
    # Load environment variables from .env file
    load_dotenv(find_dotenv())

    # Replace these variables with your database connection details
    db_name = os.environ.get('DB_NAME')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASS')
    host = os.environ.get('DB_HOST')
    port = os.environ.get('DB_PORT')

    return db_name, user, password, host, port


def check_readiness() -> bool:
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


def load_config() -> AppConfig:
    """Load the configuration from the pyproject.toml file."""
    try:
        with open('pyproject.toml') as f:
            config_data: dict[str, Any] = toml.load(f)
            tool_config: ToolConfig = config_data.get('tool', {})
            app_config: AppConfig = tool_config.get('supabase_pydantic', {})
            return app_config
    except FileNotFoundError:
        return {}


config_dict: AppConfig = load_config()


# @click.group()
# def gen():
#     """Generate models from a PostgreSQL database."""
#     click.echo('Generating models...')


# @gen.command()
# def pydantic():
#     """Generate Pydantic models."""
#     click.echo('Generating Pydantic models...')


# @gen.command()
# def sqlalchemy():
#     """Generate SQLAlchemy models."""
#     click.echo('Generating SQLAlchemy models...')


@click.command()
@click.option(
    '-d', '--directory', 'default_directory', default='entities', help='The directory to save the generated files.'
)
@click.option('-a', '--all', '_all', is_flag=True, help='Generate all model files. Overrides other flags.')
@click.option('--overwrite/--no-overwrite', help='Overwrite existing files.')
@click.option(
    '--sqlalchemy', 'generate_sqlalchemy', is_flag=True, help='Add SQLAlchemy database models to the generated files.'
)
@click.option('--fastapi-jsonapi', 'generate_jsonapi', is_flag=True, help='Generate files for FastAPI-JSONAPI.')
@click.option('--nullify-base-schema', is_flag=True, help='Force all default values in Base schema to be nullable.')
@click.option('-c', '--clean', 'cleanup', is_flag=True, help='Remove & clean the generated directory and files.')
def main(
    _all: bool,
    generate_sqlalchemy: bool,
    generate_jsonapi: bool,
    cleanup: bool,
    default_directory: str = config_dict.get('default_directory', 'entities'),
    overwrite: bool = config_dict.get('overwrite_existing_files', True),
    nullify_base_schema: bool = config_dict.get('nullify_base_schema', False),
) -> None:
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
        assert (
            db_name is not None and user is not None and password is not None and host is not None and port is not None
        ), 'Environment variables not set correctly.'
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
            framework_type=FrameWorkType.FASTAPI,
            filename=pydantic_fname,
            directory=fastapi_directory,
            enabled=True,
        ),
        'FastAPI SQLAlchemy': WriterConfig(
            file_type=OrmType.SQLALCHEMY,
            framework_type=FrameWorkType.FASTAPI,
            filename=sqlalchemy_fname,
            directory=fastapi_directory,
            enabled=generate_sqlalchemy,
        ),
        'FastAPI-JSONAPI Pydantic': WriterConfig(
            file_type=OrmType.PYDANTIC,
            framework_type=FrameWorkType.FASTAPI_JSONAPI,
            filename=pydantic_fname,
            directory=jsonapi_directory,
            enabled=generate_jsonapi,
        ),
        'FastAPI-JSONAPI SQLAlchemy': WriterConfig(
            file_type=OrmType.SQLALCHEMY,
            framework_type=FrameWorkType.FASTAPI_JSONAPI,
            filename=sqlalchemy_fname,
            directory=jsonapi_directory,
            enabled=generate_jsonapi and generate_sqlalchemy,
        ),
    }

    paths = []
    factory = FileWriterFactory()
    for job, c in jobs.items():  # c = config
        if not c.enabled:
            continue

        print(f'Generating {job} models...')
        p = factory.get_file_writer(tables, c.fpath(), c.file_type, c.framework_type).save(overwrite)
        paths.append(p)
        print(f'{job} models generated successfully: {p}')

    try:
        for p in paths:
            run_isort(p)
            format_with_ruff(p)
    except Exception as e:
        print('An error occurred while running isort.')
        print(e)


if __name__ == '__main__':
    main()
