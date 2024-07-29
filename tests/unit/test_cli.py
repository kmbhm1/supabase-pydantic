import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from supabase_pydantic.cli import cli, check_readiness, load_config


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('DB_NAME', 'test_db')
    monkeypatch.setenv('DB_USER', 'user')
    monkeypatch.setenv('DB_PASS', 'pass')
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_PORT', '5432')


def test_cli_no_args(runner):
    """Test the CLI without any arguments."""
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert 'A CLI tool for generating Pydantic models' in result.output


def test_check_readiness_success():
    env_vars = {'DB_NAME': 'test_db', 'DB_USER': 'user', 'DB_PASS': 'pass', 'DB_HOST': 'localhost', 'DB_PORT': '5432'}
    assert check_readiness(env_vars)  # Should return True


def test_check_readiness_missing_env_vars():
    """Test environment check with missing variables."""
    env_vars = {'DB_NAME': 'test_db', 'DB_USER': 'user', 'DB_PASS': None, 'DB_HOST': 'localhost', 'DB_PORT': '5432'}
    assert not check_readiness(env_vars)
    assert not check_readiness({})  # Empty dictionary


def test_check_readiness_all_env_vars_missing(mock_env_vars):
    """Test environment check with all variables set."""
    with pytest.raises(TypeError):
        check_readiness()


def test_load_config_file_not_found():
    """Test loading configuration from a non-existent file."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        config = load_config()
    assert config == {}


def test_clean_command(runner, mock_env_vars):
    """Test the clean command functionality."""
    with patch('supabase_pydantic.cli.clean_directories') as mock_clean:
        result = runner.invoke(cli, ['clean'])
        assert 'Cleaning up the project...' in result.output
        assert result.exit_code == 0
        mock_clean.assert_called_once()


def test_clean_command_handles_FileExistsError_and_FileNotFoundError(runner, mock_env_vars):
    """Test the clean command handles FileExistsError."""
    with patch('supabase_pydantic.cli.clean_directories', side_effect=FileExistsError):
        result = runner.invoke(cli, ['clean'])
        assert "Directory doesn't exist" in result.output
        assert result.exit_code == 0

    with patch('supabase_pydantic.cli.clean_directories', side_effect=FileNotFoundError):
        result = runner.invoke(cli, ['clean'])
        assert "Directory doesn't exist" in result.output
        assert result.exit_code == 0


def test_clean_command_handles_other_errors(runner, mock_env_vars):
    """Test the clean command handles other errors."""
    with patch('supabase_pydantic.cli.clean_directories', side_effect=Exception):
        result = runner.invoke(cli, ['clean'])
        assert 'An error occurred while cleaning the project' in result.output
        assert result.exit_code == 0
