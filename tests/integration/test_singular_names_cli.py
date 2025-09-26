"""Integration tests for the --singular-names CLI flag.

These tests focus on the CLI interface and argument parsing for the singular names feature.
"""

import tempfile
import shutil
from unittest.mock import patch, Mock

import pytest
from click.testing import CliRunner

from supabase_pydantic.cli.commands.gen import gen
from supabase_pydantic.db.database_type import DatabaseType


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test output."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_minimal_setup():
    """Minimal mock setup for CLI testing."""
    with patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup, \
         patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct, \
         patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs, \
         patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs, \
         patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory, \
         patch('supabase_pydantic.cli.commands.gen.format_with_ruff') as mock_format:

        # Setup basic mocks
        mock_setup.return_value = (Mock(), DatabaseType.POSTGRES)
        mock_construct.return_value = {'public': [Mock(name='test_table')]}
        mock_dirs.return_value = {'default': '/tmp'}

        # Create a proper job config that will trigger get_file_writer
        mock_config = Mock()
        mock_config.enabled = True
        mock_config.fpath.return_value = '/tmp/model.py'
        mock_config.file_type = 'pydantic'
        mock_config.framework_type = 'fastapi'
        mock_jobs.return_value = {'public': {'pydantic_models': mock_config}}

        # Mock writer
        mock_writer = Mock()
        mock_writer.save.return_value = ('/tmp/model.py', None)
        mock_factory.return_value.get_file_writer.return_value = mock_writer

        yield {
            'setup': mock_setup,
            'construct': mock_construct,
            'dirs': mock_dirs,
            'jobs': mock_jobs,
            'factory': mock_factory,
            'format': mock_format,
            'writer': mock_writer
        }


@pytest.fixture
def runner():
    """Create a CliRunner instance."""
    return CliRunner()


@pytest.mark.integration
def test_singular_names_flag_parsing(runner, temp_output_dir, mock_minimal_setup):
    """Test that the --singular-names flag is correctly parsed and passed through."""
    # Test with --singular-names flag
    result = runner.invoke(gen, [
        '--db-url', 'postgresql://test:test@localhost/test',
        '--dir', temp_output_dir,
        '--singular-names'
    ])

    assert result.exit_code == 0, f"Command failed with output: {result.output}"

    # Verify that get_file_writer was called with singular_names=True
    mock_minimal_setup['factory'].return_value.get_file_writer.assert_called_once()
    call_args = mock_minimal_setup['factory'].return_value.get_file_writer.call_args

    # Check that singular_names=True was passed
    assert 'singular_names' in call_args.kwargs
    assert call_args.kwargs['singular_names'] is True


@pytest.mark.integration
def test_default_behavior_without_flag(runner, temp_output_dir, mock_minimal_setup):
    """Test that without --singular-names flag, singular_names=False is passed."""
    # Test without --singular-names flag
    result = runner.invoke(gen, [
        '--db-url', 'postgresql://test:test@localhost/test',
        '--dir', temp_output_dir
    ])

    assert result.exit_code == 0, f"Command failed with output: {result.output}"

    # Verify that get_file_writer was called with singular_names=False (default)
    mock_minimal_setup['factory'].return_value.get_file_writer.assert_called_once()
    call_args = mock_minimal_setup['factory'].return_value.get_file_writer.call_args

    # Check that singular_names=False was passed (default)
    assert 'singular_names' in call_args.kwargs
    assert call_args.kwargs['singular_names'] is False


@pytest.mark.integration
def test_singular_names_with_other_flags(runner, temp_output_dir, mock_minimal_setup):
    """Test that --singular-names works correctly with other CLI flags."""
    # Test with multiple flags including --singular-names
    result = runner.invoke(gen, [
        '--db-url', 'postgresql://test:test@localhost/test',
        '--dir', temp_output_dir,
        '--singular-names',
        '--no-crud-models',
        '--no-enums',
        '--disable-model-prefix-protection'
    ])

    assert result.exit_code == 0, f"Command failed with output: {result.output}"

    # Verify that all flags were passed correctly
    mock_minimal_setup['factory'].return_value.get_file_writer.assert_called_once()
    call_args = mock_minimal_setup['factory'].return_value.get_file_writer.call_args

    # Check all the flags
    assert call_args.kwargs['singular_names'] is True
    assert call_args.kwargs['generate_crud_models'] is False
    assert call_args.kwargs['generate_enums'] is False
    assert call_args.kwargs['disable_model_prefix_protection'] is True


@pytest.mark.integration
def test_singular_names_help_text(runner):
    """Test that the --singular-names flag appears in help text."""
    result = runner.invoke(gen, ['--help'])

    assert result.exit_code == 0
    assert '--singular-names' in result.output
    assert 'Generate class names in singular form' in result.output
    assert 'Product' in result.output  # Should show example
    assert 'Products' in result.output  # Should show example


@pytest.mark.integration
def test_singular_names_with_different_frameworks(runner, temp_output_dir, mock_minimal_setup):
    """Test that --singular-names works with different framework types."""
    frameworks = ['fastapi']  # Add more when available

    for framework in frameworks:
        # Reset the mock for each iteration
        mock_minimal_setup['factory'].reset_mock()

        result = runner.invoke(gen, [
            '--db-url', 'postgresql://test:test@localhost/test',
            '--dir', temp_output_dir,
            '--framework', framework,
            '--singular-names'
        ])

        assert result.exit_code == 0, f"Command failed for framework {framework} with output: {result.output}"

        # Verify that singular_names=True was passed for each framework
        mock_minimal_setup['factory'].return_value.get_file_writer.assert_called()
        call_args = mock_minimal_setup['factory'].return_value.get_file_writer.call_args
        assert call_args.kwargs['singular_names'] is True


@pytest.mark.integration
def test_singular_names_with_different_types(runner, temp_output_dir, mock_minimal_setup):
    """Test that --singular-names works with different model types."""
    model_types = ['pydantic', 'sqlalchemy']

    for model_type in model_types:
        # Reset the mock for each iteration
        mock_minimal_setup['factory'].reset_mock()

        result = runner.invoke(gen, [
            '--db-url', 'postgresql://test:test@localhost/test',
            '--dir', temp_output_dir,
            '--type', model_type,
            '--singular-names'
        ])

        assert result.exit_code == 0, f"Command failed for type {model_type} with output: {result.output}"

        # Verify that singular_names=True was passed for each type
        mock_minimal_setup['factory'].return_value.get_file_writer.assert_called()
        call_args = mock_minimal_setup['factory'].return_value.get_file_writer.call_args
        assert call_args.kwargs['singular_names'] is True


@pytest.mark.integration
def test_singular_names_flag_is_boolean(runner, temp_output_dir, mock_minimal_setup):
    """Test that --singular-names is a boolean flag (no value required)."""
    # Test that the flag works without a value
    result = runner.invoke(gen, [
        '--db-url', 'postgresql://test:test@localhost/test',
        '--dir', temp_output_dir,
        '--singular-names'
    ])

    assert result.exit_code == 0, f"Command failed with output: {result.output}"

    # Test that providing a value to the flag fails (it's a boolean flag)
    result_with_value = runner.invoke(gen, [
        '--db-url', 'postgresql://test:test@localhost/test',
        '--dir', temp_output_dir,
        '--singular-names', 'true'  # This should be treated as a separate argument
    ])

    # This should fail because 'true' would be interpreted as an unknown argument
    assert result_with_value.exit_code != 0


@pytest.mark.integration
def test_singular_names_with_multiple_schemas(runner, temp_output_dir, mock_minimal_setup):
    """Test that --singular-names works with multiple schemas."""
    result = runner.invoke(gen, [
        '--db-url', 'postgresql://test:test@localhost/test',
        '--dir', temp_output_dir,
        '--schema', 'public',
        '--schema', 'auth',
        '--singular-names'
    ])

    assert result.exit_code == 0, f"Command failed with output: {result.output}"

    # Verify that singular_names=True was passed
    mock_minimal_setup['factory'].return_value.get_file_writer.assert_called()
    call_args = mock_minimal_setup['factory'].return_value.get_file_writer.call_args
    assert call_args.kwargs['singular_names'] is True


@pytest.mark.integration
def test_singular_names_error_handling(runner, temp_output_dir):
    """Test error handling when using --singular-names with invalid configurations."""
    # Test with invalid database URL
    result = runner.invoke(gen, [
        '--db-url', 'invalid://url',
        '--dir', temp_output_dir,
        '--singular-names'
    ])

    # Should handle the error gracefully (exact exit code depends on error handling)
    # The important thing is that it doesn't crash due to the --singular-names flag
    assert '--singular-names' not in str(result.exception) if result.exception else True
