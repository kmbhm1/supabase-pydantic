import os
from datetime import datetime, timezone
from pathlib import Path

from supabase_pydantic.util.constants import BASE_CLASS_POSTFIX, WriterClassType
from supabase_pydantic.util.util import chunk_text


def get_base_class_post_script(table_type: str, class_type: WriterClassType) -> str:
    """Method to generate the header for the base class."""
    post = 'View' + BASE_CLASS_POSTFIX if table_type == 'VIEW' else BASE_CLASS_POSTFIX
    return post + 'Parent' if class_type == WriterClassType.PARENT else post


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
    dt_str = datetime.now(tz=timezone.utc).strftime('%Y%m%d%H%M%S%f')
    file_name = f'{base_name}_{dt_str}.{extension}'

    return os.path.join(directory, file_name)


def get_section_comment(comment_title: str, notes: list[str] | None = None) -> str:
    """Method to generate a section of columns."""
    comment = f'# {comment_title.upper()}'
    if notes is not None and len(notes) > 0:
        chunked_notes = [chunk_text(n, 70) for n in notes]
        for cn in chunked_notes:
            cn[0] = f'\n# Note: {cn[0]}'
            comment += '\n# '.join(cn)

    return comment


def get_latest_filename(file_path: str) -> str:
    """Get the latest filename for a given file path."""
    fp = Path(file_path)
    base, ext, directory = fp.stem, fp.suffix, str(fp.parent)
    latest_file = os.path.join(directory, f'{base}_latest{ext}')

    return latest_file


def write_seed_file(seed_data: dict[str, list[list[str]]], file_path: str, overwrite: bool = False) -> list[str]:
    """Write seed data to a file."""

    fp = Path(file_path)
    base, ext, directory = fp.stem, fp.suffix, str(fp.parent)
    file_paths = [get_latest_filename(file_path)]

    if not overwrite and os.path.exists(file_path):
        file_paths.append(generate_unique_filename(base, ext, directory))

    for fpath in file_paths:
        with open(fpath, 'w') as f:
            for table_name, data in seed_data.items():
                f.write(f'-- {table_name}\n')
                headers = data[0]
                data = data[1:]
                for row in data:
                    f.write(
                        f'INSERT INTO {table_name} ({", ".join(headers)}) VALUES ({", ".join([str(r) for r in row])});\n'  # noqa: E501
                    )
                f.write('\n')

    return file_paths
