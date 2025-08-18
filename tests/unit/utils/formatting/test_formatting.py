"""Tests for formatting utilities in supabase_pydantic.utils.formatting."""

import logging
import subprocess
import pytest

from supabase_pydantic.utils.formatting import format_with_ruff, RuffNotFoundError


@pytest.mark.unit
@pytest.mark.formatting
def test_format_with_ruff_failure_fails_silently(mocker, caplog):
    """Test format_with_ruff handles CalledProcessError correctly by logging warnings."""
    error_output = 'An error occurred'
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'isort', stderr=error_output))
    # Set log level to capture warnings
    caplog.set_level(logging.WARNING)
    # Run the function that should log a warning
    format_with_ruff('non_existent_file.py')
    # Check that the error was logged
    assert error_output in caplog.text
    assert 'WARNING: An error occurred while trying to format non_existent_file.py with ruff' in caplog.text


@pytest.mark.unit
@pytest.mark.formatting
def test_format_with_ruff_file_not_found(mocker):
    """Test format_with_ruff raises RuffNotFoundError when ruff is not found."""
    # Simulate ruff executable not being found
    mocker.patch('subprocess.run', side_effect=FileNotFoundError('ruff'))

    # Check that the correct exception is raised
    with pytest.raises(RuffNotFoundError) as excinfo:
        format_with_ruff('test_file.py')

    # Check the exception message
    assert 'Ruff executable not found. Formatting skipped.' in str(excinfo.value)
    assert 'test_file.py' in str(excinfo.value)


@pytest.mark.unit
@pytest.mark.formatting
def test_ruff_not_found_error_constructor():
    """Test the RuffNotFoundError constructor."""
    # Test with default message
    error1 = RuffNotFoundError(file_path='test_file.py')
    assert error1.file_path == 'test_file.py'
    assert 'Ruff executable not found. Formatting skipped.' in str(error1)
    assert 'For file: test_file.py' in str(error1)

    # Test with custom message
    error2 = RuffNotFoundError(file_path='another_file.py', message='Custom error message')
    assert error2.file_path == 'another_file.py'
    assert 'Custom error message' in str(error2)
    assert 'For file: another_file.py' in str(error2)
