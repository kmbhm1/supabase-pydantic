"""File system utility functions for managing files and directories."""

import os
import shutil
from typing import Optional

from src.supabase_pydantic.core.constants import FrameWorkType, OrmType, WriterConfig


def clean_directory(directory: str) -> None:
    """Remove all files & directories in the specified directory."""
    if not (os.path.isdir(directory) and len(os.listdir(directory)) == 0):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'An error occurred while deleting {file_path}.')
                print(str(e))

    shutil.rmtree(directory)


def clean_directories(directories: dict[str, Optional[str]]) -> None:
    """Remove all files & directories in the specified directories."""
    for k, d in directories.items():
        if k == 'default' or d is None:
            continue

        print(f'Checking for directory: {d}')
        if not os.path.isdir(d):
            print(f'Directory "{d}" does not exist. Skipping ...')
            continue

        print(f'Directory found. Removing {d} and files...')
        clean_directory(d)
        print(f'Directory {d} removed.')

    print(f'Removing default directory {directories["default"]} ...')
    assert directories['default'] is not None
    clean_directory(directories['default'])
    print('Default directory removed.')


def get_working_directories(
    default_directory: str, frameworks: tuple, auto_create: bool = False
) -> dict[str, Optional[str]]:
    """Get the directories for the generated files.

    Args:
        default_directory: The base directory for generated files
        frameworks: Tuple of framework names to create directories for
        auto_create: Whether to create the directories if they don't exist

    Returns:
        A dictionary mapping framework names to directory paths
    """
    if not os.path.exists(default_directory) or not os.path.isdir(default_directory):
        print(f'Directory {default_directory} does not exist.')

    directories = {
        'default': default_directory,
        'fastapi': None if 'fastapi' not in frameworks else os.path.join(default_directory, 'fastapi'),
    }

    if auto_create:
        create_directories_if_not_exist(directories)

    return directories


def create_directories_if_not_exist(directories: dict[str, Optional[str]]) -> None:
    """Create the directories for the generated files if they do not exist.

    Args:
        directories: Dictionary mapping framework names to directory paths
    """
    # Check if the directory exists, if not, create it
    for _, d in directories.items():
        if d is None:
            continue
        if not os.path.exists(d) or not os.path.isdir(d):
            print(f'Creating directory: {d}')
            os.makedirs(d)


def get_standard_jobs(
    models: tuple[str], frameworks: tuple[str], dirs: dict[str, Optional[str]], schemas: tuple[str, ...] = ('public',)
) -> dict[str, dict[str, WriterConfig]]:
    """Get the standard jobs for the writer.

    This function sets up configuration for generating various output files.

    Args:
        models: Tuple of model types to generate (e.g., 'pydantic', 'sqlalchemy')
        frameworks: Tuple of frameworks to generate for (e.g., 'fastapi')
        dirs: Dictionary mapping framework names to directory paths
        schemas: Tuple of database schemas to generate for

    Returns:
        A nested dictionary of schema names to job names to writer configurations
    """
    jobs: dict[str, dict[str, WriterConfig]] = {}

    for schema in schemas:
        # Set the file names
        pydantic_fname, sqlalchemy_fname = f'schema_{schema}.py', f'database_{schema}.py'

        # Add the jobs
        if 'fastapi' in dirs and dirs['fastapi'] is not None:
            jobs[schema] = {
                'Pydantic': WriterConfig(
                    file_type=OrmType.PYDANTIC,
                    framework_type=FrameWorkType.FASTAPI,
                    filename=pydantic_fname,
                    directory=dirs['fastapi'],
                    enabled='pydantic' in models and 'fastapi' in frameworks,
                ),
                'SQLAlchemy': WriterConfig(
                    file_type=OrmType.SQLALCHEMY,
                    framework_type=FrameWorkType.FASTAPI,
                    filename=sqlalchemy_fname,
                    directory=dirs['fastapi'],
                    enabled='sqlalchemy' in models and 'fastapi' in frameworks,
                ),
            }

    return jobs


def local_default_env_configuration() -> dict[str, Optional[str]]:
    """Get the default environment variables for a local database connection.

    Returns:
        A dictionary of environment variable names to values
    """
    return {
        'DB_NAME': 'postgres',
        'DB_USER': 'postgres',
        'DB_PASS': 'postgres',
        'DB_HOST': 'localhost',
        'DB_PORT': '54322',
    }
