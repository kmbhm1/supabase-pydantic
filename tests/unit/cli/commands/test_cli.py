from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from supabase_pydantic.cli import cli
from supabase_pydantic.cli.common import check_readiness, load_config


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


@pytest.mark.unit
@pytest.mark.cli
def test_cli_no_args(runner):
    """Test the CLI without any arguments."""
    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert 'A CLI tool for generating Pydantic models' in result.output


@pytest.mark.unit
@pytest.mark.cli
def test_check_readiness_success():
    env_vars = {'DB_NAME': 'test_db', 'DB_USER': 'user', 'DB_PASS': 'pass', 'DB_HOST': 'localhost', 'DB_PORT': '5432'}
    assert check_readiness(env_vars)  # Should return True


@pytest.mark.unit
@pytest.mark.cli
def test_check_readiness_missing_env_vars():
    """Test environment check with missing variables."""
    env_vars = {'DB_NAME': 'test_db', 'DB_USER': 'user', 'DB_PASS': None, 'DB_HOST': 'localhost', 'DB_PORT': '5432'}
    assert not check_readiness(env_vars)
    assert not check_readiness({})  # Empty dictionary


@pytest.mark.unit
@pytest.mark.cli
def test_check_readiness_all_env_vars_missing(mock_env_vars):
    """Test environment check with all variables set."""
    with pytest.raises(TypeError):
        check_readiness()


@pytest.mark.unit
@pytest.mark.cli
def test_load_config_file_not_found():
    """Test loading configuration from a non-existent file."""
    with patch('builtins.open', side_effect=FileNotFoundError):
        config = load_config()
    assert config == {}


@pytest.mark.unit
@pytest.mark.cli
def test_clean_command(runner, mock_env_vars):
    """Test the clean command functionality."""
    with patch('supabase_pydantic.cli.commands.clean.clean_directories') as mock_clean:
        result = runner.invoke(cli, ['clean'])
        assert 'Cleaning up the project...' in result.output
        assert result.exit_code == 0
        mock_clean.assert_called_once()


@pytest.mark.unit
@pytest.mark.cli
def test_clean_command_handles_FileExistsError_and_FileNotFoundError(runner, mock_env_vars):
    """Test the clean command handles FileExistsError."""
    with patch('supabase_pydantic.cli.commands.clean.clean_directories', side_effect=FileExistsError):
        result = runner.invoke(cli, ['clean'])
        assert "Directory doesn't exist" in result.output
        assert result.exit_code == 0

    with patch('supabase_pydantic.cli.commands.clean.clean_directories', side_effect=FileNotFoundError):
        result = runner.invoke(cli, ['clean'])
        assert "Directory doesn't exist" in result.output
        assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_clean_command_handles_other_errors(runner, mock_env_vars):
    """Test the clean command handles other errors."""
    with patch('supabase_pydantic.cli.commands.clean.clean_directories', side_effect=Exception):
        result = runner.invoke(cli, ['clean'])
        assert 'An error occurred while cleaning the project:' in result.output
        assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_gen_command_with_invalid_db_url(runner):
    """Test gen command with invalid database URL."""
    result = runner.invoke(cli, ['gen', '--db-url', 'invalid_url'])
    assert 'PostgreSQL connection URL must start with' in result.output
    assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_gen_command_with_valid_db_url(runner):
    """Test gen command with valid database URL."""
    with (
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
        patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs,
        patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs,
        patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory,
    ):
        mock_construct.return_value = {'public': [MagicMock(name='table1')]}
        mock_dirs.return_value = {'default': '/tmp'}
        mock_jobs.return_value = {'public': {'pydantic': MagicMock(enabled=True)}}
        mock_writer = mock_factory.return_value.get_file_writer.return_value
        mock_writer.save.return_value = ('path1.py', None)

        result = runner.invoke(
            cli, ['gen', '--db-url', 'postgresql://user:pass@localhost:5432/db', '--schema', 'public']
        )
        assert 'Successfully established connection parameters for postgres' in result.output
        assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_clean_command_2(runner, mock_env_vars):
    """Test the clean command functionality."""
    with patch('supabase_pydantic.cli.commands.clean.clean_directories') as mock_clean:
        result = runner.invoke(cli, ['clean'])
        assert 'Cleaning up the project...' in result.output
        assert result.exit_code == 0
        mock_clean.assert_called_once()


@pytest.mark.unit
@pytest.mark.cli
def test_gen_command_with_empty_schemas(runner):
    """Test gen command when schemas have no tables."""
    with (
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
        patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs,
        patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs,
        patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory,
    ):
        mock_construct.return_value = {'public': [], 'schema2': []}
        mock_dirs.return_value = {'default': '/tmp'}
        mock_jobs.return_value = {}
        mock_writer = mock_factory.return_value.get_file_writer.return_value
        mock_writer.save.return_value = ('path1.py', None)

        result = runner.invoke(cli, ['gen', '--local', '--schema', 'public', '--schema', 'schema2'])
        assert 'The following schemas have no tables and will be skipped' in result.output
        assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_gen_command_with_tables(runner):
    """Test gen command with tables in schema."""
    with (
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
        patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs,
        patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs,
        patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory,
        patch('supabase_pydantic.cli.commands.gen.format_with_ruff') as mock_ruff,
    ):
        table_info = MagicMock()
        table_info.name = 'table1'
        mock_construct.return_value = {'public': [table_info]}
        mock_dirs.return_value = {'default': '/tmp'}

        writer_config = MagicMock()
        writer_config.enabled = True
        writer_config.fpath.return_value = '/tmp/models.py'
        mock_jobs.return_value = {'public': {'pydantic': writer_config}}

        mock_writer = mock_factory.return_value.get_file_writer.return_value
        mock_writer.save.return_value = ('path1.py', None)

        result = runner.invoke(cli, ['gen', '--local'])

        assert result.exit_code == 0
        mock_ruff.assert_called_once()


@pytest.mark.unit
@pytest.mark.cli
def test_gen_command_with_seed_data(runner):
    """Test gen command with seed data generation."""
    with (
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
        patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs,
        patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs,
        patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory,
        patch('supabase_pydantic.cli.commands.gen.generate_seed_data') as mock_seed,
        patch('supabase_pydantic.cli.commands.gen.write_seed_file') as mock_write_seed,
    ):
        table_info = MagicMock()
        table_info.name = 'table1'
        mock_construct.return_value = {'public': [table_info]}
        mock_dirs.return_value = {'default': '/tmp'}

        writer_config = MagicMock()
        writer_config.enabled = True
        writer_config.fpath.return_value = '/tmp/models.py'
        mock_jobs.return_value = {'public': {'pydantic': writer_config}}

        mock_writer = mock_factory.return_value.get_file_writer.return_value
        mock_writer.save.return_value = ('path1.py', None)
        mock_seed.return_value = {'table1': [{'id': 1}]}
        mock_write_seed.return_value = ['seed.sql']

        result = runner.invoke(cli, ['gen', '--local', '--seed', '--schema', 'public'])

        assert result.exit_code == 0
        mock_seed.assert_called_once()
        mock_write_seed.assert_called_once()


@pytest.mark.unit
@pytest.mark.cli
def test_gen_command_with_seed_data_no_tables(runner):
    """Test gen command with seed data generation but no tables."""
    with (
        patch('re.match', return_value=True),
        patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct,
        patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs,
        patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs,
        patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory,
        patch('supabase_pydantic.cli.commands.gen.generate_seed_data') as mock_seed,
        patch('supabase_pydantic.utils.formatting.format_with_ruff'),
        patch('supabase_pydantic.utils.io.clean_directories'),
        patch(
            'os.environ',
            {'DB_NAME': 'test_db', 'DB_USER': 'user', 'DB_PASS': 'pass', 'DB_HOST': 'localhost', 'DB_PORT': '5432'},
        ),
    ):
        mock_construct.return_value = {'public': []}
        mock_dirs.return_value = {'default': '/tmp'}

        mock_jobs.return_value = {}
        mock_writer = mock_factory.return_value.get_file_writer.return_value
        mock_writer.save.return_value = ('path1.py', None)
        mock_seed.return_value = {}

        result = runner.invoke(cli, ['gen', '--local', '--seed', '--schema', 'public'])

        assert result.exit_code == 0
        mock_seed.assert_not_called()
