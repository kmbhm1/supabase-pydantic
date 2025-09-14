import logging
import subprocess

# Get Logger
logger = logging.getLogger(__name__)


class RuffNotFoundError(Exception):
    """Custom exception raised when the ruff executable is not found."""

    def __init__(self, file_path: str, message: str = 'Ruff executable not found. Formatting skipped.'):
        self.file_path = file_path
        self.message = f'{message} For file: {file_path}'
        super().__init__(self.message)


def format_with_ruff(file_path: str) -> None:
    """Run the ruff formatter, import sorter, and fixer on a specified Python file."""
    try:
        # First run ruff check --fix to handle imports and other issues
        import_result = subprocess.run(
            ['ruff', 'check', '--select', 'I', '--fix', file_path], text=True, capture_output=True
        )
        if import_result.returncode != 0:
            logger.debug(f'Ruff import sorting had issues: {import_result.stderr}')

        # Then run ruff format for code formatting
        format_result = subprocess.run(['ruff', 'format', file_path], text=True, capture_output=True)
        if format_result.returncode != 0:
            logger.debug(f'Ruff formatting had issues: {format_result.stderr}')

        # Finally run ruff check --fix for any remaining issues
        fix_result = subprocess.run(['ruff', 'check', '--fix', file_path], text=True, capture_output=True)
        if fix_result.returncode != 0:
            logger.debug(f'Ruff fixing had issues: {fix_result.stderr}')

        # Even if there were warnings, the file is likely formatted correctly
        logger.info(f'File formatted successfully: {file_path}')

    except subprocess.CalledProcessError as e:
        logger.warning(f'An error occurred while trying to format {file_path} with ruff:')
        logger.warning(e.stderr if e.stderr else 'No stderr output available')
        logger.warning('The file was generated, but not formatted.')
    except FileNotFoundError:
        raise RuffNotFoundError(file_path=file_path)
