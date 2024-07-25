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
