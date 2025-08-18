"""Tests for cli/common.py functions."""

from unittest.mock import patch, mock_open
from inspect import signature

from supabase_pydantic.cli.common import check_readiness, load_config, common_options


def test_check_readiness_valid_env_vars():
    """Test check_readiness with valid env vars."""
    env_vars = {'DB_HOST': 'localhost', 'DB_PORT': '5432', 'DB_USER': 'postgres'}
    with patch('logging.debug') as mock_debug:
        result = check_readiness(env_vars)
        assert result is True
        mock_debug.assert_called_with('All required environment variables are set')


def test_check_readiness_empty_env_vars():
    """Test check_readiness with empty env vars."""
    with patch('logging.error') as mock_error:
        result = check_readiness({})
        assert result is False
        mock_error.assert_called_with('No environment variables provided.')


def test_check_readiness_missing_env_vars():
    """Test check_readiness with missing env vars."""
    env_vars = {'DB_HOST': 'localhost', 'DB_PORT': None, 'DB_USER': 'postgres'}
    with patch('logging.error') as mock_error:
        result = check_readiness(env_vars)
        assert result is False
        mock_error.assert_called_with(
            'Environment variables not set correctly. DB_PORT is missing. Please set it in .env file.'
        )


def test_load_config_from_pyproject():
    """Test loading config from pyproject.toml."""
    mock_config = {'tool': {'supabase_pydantic': {'output_dir': './models', 'schemas': ['public']}}}

    with patch('builtins.open', mock_open()) as mock_file:
        with patch('toml.load', return_value=mock_config) as mock_toml:
            config = load_config()

            mock_file.assert_called_once_with('pyproject.toml')
            mock_toml.assert_called_once()
            assert config == {'output_dir': './models', 'schemas': ['public']}


def test_load_config_from_custom_toml():
    """Test loading config from custom toml file."""
    mock_config = {'tool': {'supabase_pydantic': {'output_dir': './custom', 'schemas': ['custom']}}}

    with patch('builtins.open', mock_open()) as mock_file:
        with patch('toml.load', return_value=mock_config) as mock_toml:
            config = load_config('config.toml')

            mock_file.assert_called_once_with('config.toml')
            mock_toml.assert_called_once()
            assert config == {'output_dir': './custom', 'schemas': ['custom']}


def test_load_config_from_yaml():
    """Test loading config from yaml file."""
    mock_config = {'output_dir': './yaml_models', 'schemas': ['yaml']}

    with patch('builtins.open', mock_open()) as mock_file:
        with patch('yaml.safe_load', return_value=mock_config) as mock_yaml:
            config = load_config('config.yaml')

            mock_file.assert_called_once_with('config.yaml')
            mock_yaml.assert_called_once()
            assert config == {'output_dir': './yaml_models', 'schemas': ['yaml']}


def test_load_config_file_not_found():
    """Test load_config when file is not found."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        with patch('click.echo') as mock_echo:
            config = load_config('nonexistent.toml')

            mock_echo.assert_called_once_with('Config file not found: nonexistent.toml')
            assert config == {}


def test_load_config_pyproject_not_found():
    """Test load_config when pyproject.toml is not found."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        config = load_config()
        assert config == {}


def test_common_options():
    """Test common_options decorator."""

    @common_options
    def dummy_command(config=None):
        return config

    # In this case common_options just wraps the function with click options
    # but doesn't convert it to a click.Command - that would happen when used with @click.command()
    # So we can check that the function signature includes our options
    sig = signature(dummy_command)
    assert 'config' in sig.parameters

    # Test that we can call the function
    result = dummy_command(config='test')
    assert result == 'test'
