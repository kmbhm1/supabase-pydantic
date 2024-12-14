import os
import shutil
from typing import Any

from supabase_pydantic.util.constants import (
    PYDANTIC_TYPE_MAP,
    SQLALCHEMY_TYPE_MAP,
    SQLALCHEMY_V2_TYPE_MAP,
    FrameWorkType,
    OrmType,
    WriterConfig,
)

# string helpers


def to_pascal_case(string: str) -> str:
    """Converts a string to PascalCase."""
    words = string.split('_')
    camel_case = ''.join(word.capitalize() for word in words)
    return camel_case


def chunk_text(text: str, nchars: int = 79) -> list[str]:
    """Split text into lines with a maximum number of characters."""
    words = text.split()  # Split the text into words
    lines: list[str] = []  # This will store the final lines
    current_line: list[str] = []  # This will store words for the current line

    for word in words:
        # Check if adding the next word would exceed the length limit
        if (sum(len(w) for w in current_line) + len(word) + len(current_line)) > nchars:
            # If adding the word would exceed the limit, join current_line into a string and add to lines
            lines.append(' '.join(current_line))
            current_line = [word]  # Start a new line with the current word
        else:
            current_line.append(word)  # Add the word to the current line

    # Add the last line to lines if any words are left unadded
    if current_line:
        lines.append(' '.join(current_line))

    return lines


# enum helpers


def get_enum_member_from_string(cls: Any, value: str) -> Any:
    """Get an Enum member from a string value."""
    value_lower = value.lower()
    for member in cls:
        if member.value == value_lower:
            return member
    raise ValueError(f"'{value}' is not a valid {cls.__name__}")


# type map helpers


def adapt_type_map(
    postgres_type: str,
    default_type: tuple[str, str | None],
    type_map: dict[str, tuple[str, str | None]],
) -> tuple[str, str | None]:
    """Adapt a PostgreSQL data type to a Pydantic and SQLAlchemy type."""
    array_suffix = '[]'
    if postgres_type.endswith(array_suffix):
        base_type = postgres_type[: -len(array_suffix)]
        sqlalchemy_type, import_statement = type_map.get(base_type, default_type)
        adapted_type = f'ARRAY({sqlalchemy_type})'
        import_statement = (
            f'{import_statement}, ARRAY' if import_statement else 'from sqlalchemy.dialects.postgresql import ARRAY'
        )
    else:
        adapted_type, import_statement = type_map.get(postgres_type, default_type)

    return (adapted_type, import_statement)


def get_sqlalchemy_type(
    postgres_type: str, default: tuple[str, str | None] = ('String', 'from sqlalchemy import String')
) -> tuple[str, str | None]:
    """Get the SQLAlchemy type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, SQLALCHEMY_TYPE_MAP)


def get_sqlalchemy_v2_type(
    postgres_type: str, default: tuple[str, str | None] = ('String,str', 'from sqlalchemy import String')
) -> tuple[str, str, str | None]:
    """Get the SQLAlchemy v2 type from the PostgreSQL type."""
    both_types, imports = adapt_type_map(postgres_type, default, SQLALCHEMY_V2_TYPE_MAP)
    sql, py = both_types.split(',')
    return (sql, py, imports)


def get_pydantic_type(postgres_type: str, default: tuple[str, str | None] = ('Any', None)) -> tuple[str, str | None]:
    """Get the Pydantic type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, PYDANTIC_TYPE_MAP)


# file helpers


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


def clean_directories(directories: dict[str, str | None]) -> None:
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
) -> dict[str, str | None]:
    """Get the directories for the generated files."""
    if not os.path.exists(default_directory) or not os.path.isdir(default_directory):
        print(f'Directory {default_directory} does not exist.')

    directories = {
        'default': default_directory,
        'fastapi': None if 'fastapi' not in frameworks else os.path.join(default_directory, 'fastapi'),
    }

    if auto_create:
        create_directories_if_not_exist(directories)

    return directories


def create_directories_if_not_exist(directories: dict[str, str | None]) -> None:
    """Create the directories for the generated files if they do not exist."""
    # Check if the directory exists, if not, create it
    for _, d in directories.items():
        if d is None:
            continue
        if not os.path.exists(d) or not os.path.isdir(d):
            print(f'Creating directory: {d}')
            os.makedirs(d)


# job helpers


def get_standard_jobs(
    models: tuple[str], frameworks: tuple[str], dirs: dict[str, str | None], schemas: tuple[str, ...] = ('public',)
) -> dict[str, dict[str, WriterConfig]]:
    """Get the standard jobs for the writer."""

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


def local_default_env_configuration() -> dict[str, str | None]:
    """Get the environment variables for a local connection."""
    return {
        'DB_NAME': 'postgres',
        'DB_USER': 'postgres',
        'DB_PASS': 'postgres',
        'DB_HOST': 'localhost',
        'DB_PORT': '54322',
    }
