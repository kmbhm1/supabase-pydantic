"""Code formatting utilities."""

import subprocess


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
        print('Error during Ruff processing:')
        print(e.stderr)  # Print any error output from ruff
