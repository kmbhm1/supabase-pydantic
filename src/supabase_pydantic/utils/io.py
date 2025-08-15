import logging
import os
import shutil

# Get Logger
logger = logging.getLogger(__name__)


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
                logger.error(f'An error occurred while deleting {file_path}.')
                logger.error(str(e))

    shutil.rmtree(directory)


def clean_directories(directories: dict[str, str | None]) -> None:
    """Remove all files & directories in the specified directories."""
    for k, d in directories.items():
        if k == 'default' or d is None:
            continue

        logger.info(f'Checking for directory: {d}')
        if not os.path.isdir(d):
            logger.warning(f'Directory "{d}" does not exist. Skipping ...')
            continue

        logger.info(f'Directory found. Removing {d} and files...')
        clean_directory(d)
        logger.info(f'Directory {d} removed.')

    logger.info(f'Removing default directory {directories["default"]} ...')
    assert directories['default'] is not None
    clean_directory(directories['default'])
    logger.info('Default directory removed.')


def get_working_directories(
    default_directory: str, frameworks: tuple, auto_create: bool = False
) -> dict[str, str | None]:
    """Get the directories for the generated files."""
    if not os.path.exists(default_directory) or not os.path.isdir(default_directory):
        logger.warning(f'Directory {default_directory} does not exist.')

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
            logger.info(f'Creating directory: {d}')
            os.makedirs(d)
