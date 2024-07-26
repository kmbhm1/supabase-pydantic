import os

from supabase_pydantic.util.constants import BASE_CLASS_POSTFIX
from supabase_pydantic.util.util import chunk_text


def get_base_class_post_script(table_type: str, nullable: bool) -> str:
    """Method to generate the header for the base class."""
    post = 'View' + BASE_CLASS_POSTFIX if table_type == 'VIEW' else BASE_CLASS_POSTFIX
    return post + 'Nullable' if nullable else post


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


def get_section_comment(comment_title: str, notes: list[str] | None = None) -> str:
    """Method to generate a section of columns."""
    comment = '#' * 30 + f' {comment_title}'
    if notes is not None and len(notes) > 0:
        chunked_notes = [chunk_text(n, 70) for n in notes]
        for cn in chunked_notes:
            cn[0] = f'\n# Note: {cn[0]}'
            comment += '\n# '.join(cn)

    return comment
