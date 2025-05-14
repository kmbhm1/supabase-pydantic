"""File and directory operation utilities."""

import os
import shutil


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
    # First check if any directories exist
    any_exists = False
    for k, d in directories.items():
        if d is None:
            continue
        if os.path.isdir(d):
            any_exists = True
            break

    if not any_exists:
        print('Directory entities does not exist.')

    # Process subdirectories
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

    # Process default directory
    default_dir = directories.get('default')
    if default_dir is None:
        return

    print(f'Removing default directory {default_dir} ...')
    if not os.path.isdir(default_dir):
        print(f'Directory doesn\'t exist: "{default_dir}". Exiting...')
        return

    clean_directory(default_dir)
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
