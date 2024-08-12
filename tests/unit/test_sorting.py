import pytest
import subprocess
from supabase_pydantic.util.sorting import format_with_ruff, run_isort


def test_run_isort_success(mocker, capsys):
    """Test run_isort succeeds without errors."""
    mocker.patch('subprocess.run')
    subprocess.run.return_value = subprocess.CompletedProcess(
        args=['isort', 'dummy_file.py'], returncode=0, stdout='Done', stderr=''
    )

    run_isort('dummy_file.py')
    _, err = capsys.readouterr()
    assert err == '' or err is None


def test_run_isort_failure_fails_silently(mocker, capsys):
    """Test run_isort handles CalledProcessError correctly."""
    error_output = 'An error occurred'
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'isort', stderr=error_output))

    run_isort('non_existent_file.py')
    out, err = capsys.readouterr()
    assert error_output in out
    assert error_output not in err


def test_format_with_ruff_success(mocker, capsys):
    """Test run_isort succeeds without errors."""
    mocker.patch('subprocess.run')
    subprocess.run.return_value = subprocess.CompletedProcess(
        args=['isort', 'dummy_file.py'], returncode=0, stdout='Done', stderr=''
    )

    format_with_ruff('dummy_file.py')
    _, err = capsys.readouterr()
    assert err == '' or err is None


def test_format_with_ruff_failure_fails_silently(mocker, capsys):
    """Test run_isort handles CalledProcessError correctly."""
    error_output = 'An error occurred'
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'isort', stderr=error_output))

    format_with_ruff('non_existent_file.py')
    out, err = capsys.readouterr()
    assert error_output in out
    assert error_output not in err
