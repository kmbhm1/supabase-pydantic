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
        _ = subprocess.run(
            ['ruff', 'check', '--select', 'I', '--fix', file_path], check=True, text=True, capture_output=True
        )

        # Then run ruff format for code formatting
        _ = subprocess.run(['ruff', 'format', file_path], check=True, text=True, capture_output=True)

        # Finally run ruff check --fix for any remaining issues
        _ = subprocess.run(['ruff', 'check', '--fix', file_path], check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f'WARNING: An error occurred while trying to format {file_path} with ruff:')
        logger.warning(e.stderr)
        logger.warning('The file was generated, but not formatted.')
    except FileNotFoundError:
        raise RuffNotFoundError(file_path=file_path)
