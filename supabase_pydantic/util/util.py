import os
import shutil

from supabase_pydantic.util.constants import PYDANTIC_TYPE_MAP, SQLALCHEMY_TYPE_MAP


def adapt_type_map(
    postgres_type: str, default_type: tuple[str, str | None], type_map: dict[str, tuple[str, str | None]]
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
    postgres_type: str, default: tuple[str, str | None] = ('String', None)
) -> tuple[str, str | None]:
    """Get the SQLAlchemy type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, SQLALCHEMY_TYPE_MAP)


def get_pydantic_type(postgres_type: str, default: tuple[str, str | None] = ('Any', None)) -> tuple[str, str | None]:
    """Get the Pydantic type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, PYDANTIC_TYPE_MAP)


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

    return file_path


def clean_directory(directory: str) -> None:
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


def clean_directories(directories: list) -> None:
    """Remove all files & directories in the specified directories."""
    for d in directories:
        print(f'Checking for directory: {d}')
        if not os.path.isdir(d):
            print(f'Directory {d} does not exist.')
            return

        print(f'Cleaning directory: {d}')
        clean_directory(d)
