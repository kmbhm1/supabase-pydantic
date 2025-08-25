"""Tests for the gen.py CLI command module."""

from unittest.mock import patch, Mock, ANY

import pytest
from click.testing import CliRunner

from supabase_pydantic.cli.commands.gen import gen
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import MySQLConnectionParams, PostgresConnectionParams, TableInfo


@pytest.fixture
def mock_setup_database_connection():
    """Mock the database connection setup function."""
    with patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup:
        # Create a mock connection params
        mock_postgres_params = Mock(spec=PostgresConnectionParams)
        mock_postgres_params.to_dict.return_value = {'db_url': 'postgresql://user:pass@localhost/testdb'}

        # Return mock connection params and Postgres database type
        mock_setup.return_value = (mock_postgres_params, DatabaseType.POSTGRES)
        yield mock_setup


@pytest.fixture
def mock_construct_tables():
    """Mock the construct_tables function."""
    with patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct:
        # Create mock table info
        mock_tables = {
            'public': [
                TableInfo(name='users', schema='public', table_type='BASE TABLE'),
                TableInfo(name='posts', schema='public', table_type='BASE TABLE'),
            ]
        }
        mock_construct.return_value = mock_tables
        yield mock_construct


@pytest.fixture
def mock_file_writer_factory():
    """Mock the FileWriterFactory class."""
    with patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory_class:
        mock_factory = Mock()
        mock_factory_class.return_value = mock_factory

        # Mock the writer
        mock_writer = Mock()
        mock_factory.get_file_writer.return_value = mock_writer

        # Mock save method to return a file path
        mock_writer.save.return_value = ('/path/to/generated/model.py', None)

        yield mock_factory


@pytest.fixture
def mock_get_working_directories():
    """Mock the get_working_directories function."""
    with patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs:
        mock_dirs.return_value = {'default': '/path/to/entities', 'fastapi': '/path/to/entities/fastapi'}
        yield mock_dirs


@pytest.fixture
def mock_format_with_ruff():
    """Mock the format_with_ruff function."""
    with patch('supabase_pydantic.cli.commands.gen.format_with_ruff') as mock_format:
        yield mock_format


@pytest.fixture
def mock_generate_seed_data():
    """Mock the generate_seed_data function."""
    with patch('supabase_pydantic.cli.commands.gen.generate_seed_data') as mock_generate:
        mock_generate.return_value = {'users': [{'id': 1, 'name': 'Test User'}]}
        yield mock_generate


@pytest.fixture
def mock_write_seed_file():
    """Mock the write_seed_file function."""
    with patch('supabase_pydantic.cli.commands.gen.write_seed_file') as mock_write:
        mock_write.return_value = ['/path/to/entities/seed_public.sql']
        yield mock_write


@pytest.fixture
def mock_get_standard_jobs():
    """Mock the get_standard_jobs function."""
    with patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs:
        # Create mock job configuration
        mock_config = Mock()
        mock_config.enabled = True
        mock_config.fpath.return_value = '/path/to/entities/model.py'
        mock_config.file_type = 'python'
        mock_config.framework_type = 'fastapi'

        # Create mock job dictionary
        mock_jobs.return_value = {'public': {'pydantic_models': mock_config}}
        yield mock_jobs


@pytest.fixture
def runner():
    """Create a CliRunner instance."""
    return CliRunner()


@pytest.mark.unit
@pytest.mark.cli
def test_gen_basic_postgres_db_url(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
    mock_format_with_ruff,
):
    """Test basic gen command with postgres db_url."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify the setup_database_connection call
    mock_setup_database_connection.assert_called_once_with(
        conn_type=DatabaseConnectionType.DB_URL,
        db_type=None,
        env_file=None,
        local=False,
        db_url='postgresql://user:pass@localhost/testdb',
    )

    # Verify the construct_tables call
    mock_construct_tables.assert_called_once()

    # Verify the FileWriterFactory was used correctly
    mock_file_writer_factory.get_file_writer.assert_called_once()

    # Verify formatting was attempted
    assert mock_format_with_ruff.call_count == 1


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_local_connection(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with local connection."""
    # Run the command
    result = runner.invoke(gen, ['--local'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify the setup_database_connection call with local=True
    mock_setup_database_connection.assert_called_once_with(
        conn_type=DatabaseConnectionType.LOCAL, db_type=None, env_file=None, local=True, db_url=None
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_explicit_db_type(runner, mock_setup_database_connection, mock_construct_tables):
    """Test gen command with explicitly specified database type."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--db-type', 'postgres'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify the setup_database_connection call with specified database type
    mock_setup_database_connection.assert_called_once_with(
        conn_type=DatabaseConnectionType.DB_URL,
        db_type=DatabaseType.POSTGRES,
        env_file=None,
        local=False,
        db_url='postgresql://user:pass@localhost/testdb',
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_mysql_db_type(runner, mock_setup_database_connection):
    """Test gen command with MySQL database type."""
    # Configure the mock to return MySQL params
    mock_mysql_params = Mock(spec=MySQLConnectionParams)
    mock_mysql_params.db_url = 'mysql://user:pass@localhost/testdb'
    mock_mysql_params.dbname = 'testdb'
    mock_mysql_params.to_dict.return_value = {'db_url': 'mysql://user:pass@localhost/testdb'}

    mock_setup_database_connection.return_value = (mock_mysql_params, DatabaseType.MYSQL)

    with patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct:
        # Create mock MySQL tables
        mock_tables = {'testdb': [TableInfo(name='users', schema='testdb', table_type='BASE TABLE')]}
        mock_construct.return_value = mock_tables

        # Run the command
        result = runner.invoke(gen, ['--db-url', 'mysql://user:pass@localhost/testdb', '--db-type', 'mysql'])

        # Check that the command was successful
        assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_invalid_db_type(runner):
    """Test gen command with invalid database type."""
    # Run the command
    result = runner.invoke(
        gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--db-type', 'invalid'], catch_exceptions=True
    )

    # Command should complete but log an error
    assert result.exit_code == 2
    assert 'Error: Invalid value for' in result.output
    assert 'invalid' in result.output


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_multiple_schemas(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with multiple schemas."""
    # Run the command
    result = runner.invoke(
        gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--schema', 'public', '--schema', 'auth']
    )

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify construct_tables was called with the correct schemas
    mock_construct_tables.assert_called_once_with(
        conn_type=ANY,
        db_type=ANY,
        schemas=('public', 'auth'),
        disable_model_prefix_protection=False,
        connection_params=ANY,
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_all_schemas(runner, mock_setup_database_connection, mock_construct_tables):
    """Test gen command with all schemas flag."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--all-schemas'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify construct_tables was called with wildcard schema
    mock_construct_tables.assert_called_once_with(
        conn_type=ANY, db_type=ANY, schemas=('*',), disable_model_prefix_protection=False, connection_params=ANY
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_models_and_frameworks(
    runner, mock_setup_database_connection, mock_construct_tables, mock_get_working_directories, mock_get_standard_jobs
):
    """Test gen command with specified models and frameworks."""

    # Configure mock to return a valid connection
    mock_params = PostgresConnectionParams(dbname='testdb', user='user', password='pass', host='localhost', port='5432')
    mock_setup_database_connection.return_value = (mock_params, DatabaseType.POSTGRES)

    mock_tables = {'public': [TableInfo(name='users', schema='public', table_type='BASE TABLE')]}
    mock_construct_tables.return_value = mock_tables

    # Set up mock directory
    mock_get_working_directories.return_value = {'default': '/path/to/dir'}

    # Set up mock config for get_standard_jobs
    mock_config = Mock()
    mock_config.enabled = True
    mock_config.fpath.return_value = '/path/to/dir/model.py'
    mock_config.file_type = 'pydantic'
    mock_config.framework_type = None

    # Set up jobs for public schema
    mock_get_standard_jobs.return_value = {'public': {'pydantic_models': mock_config}}

    # Mock FileWriterFactory
    with patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory:
        mock_writer = Mock()
        mock_writer.save.return_value = ('/path/to/dir/model.py', None)
        mock_factory.return_value.get_file_writer.return_value = mock_writer

        # Mock the formatter to avoid errors
        with patch('supabase_pydantic.cli.commands.gen.format_with_ruff'):
            # Run the command with required options
            # Use either --local or --db-url since they're in a RequiredMutuallyExclusiveOptionGroup
            # Add the --local flag explicitly to satisfy Click's parameter validation
            result = runner.invoke(
                gen,
                [
                    '--local',  # Using --local instead of --db-url to simplify the test
                    '--type',
                    'pydantic',
                    '--framework',
                    'fastapi',
                ],
            )

            # Since we've mocked all dependencies successfully, the command should exit with code 0
            assert result.exit_code == 0, f'Command failed with output: {result.output}'

            # Verify get_working_directories was called with correct frameworks
            mock_get_working_directories.assert_called_once_with(ANY, ('fastapi',), auto_create=True)

            # Verify get_standard_jobs was called with correct models and frameworks
            mock_get_standard_jobs.assert_called_once_with(('pydantic',), ('fastapi',), ANY, ('public',))


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_seed_data(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
    mock_generate_seed_data,
    mock_write_seed_file,
):
    """Test gen command with seed data generation."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--seed'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify seed data generation was called
    mock_generate_seed_data.assert_called_once()
    mock_write_seed_file.assert_called_once()


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_empty_seed_data(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with empty seed data generation."""
    with patch('supabase_pydantic.cli.commands.gen.generate_seed_data') as mock_generate:
        # Return empty seed data
        mock_generate.return_value = {}

        # Run the command
        result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--seed'])

        # Check that the command was successful but warning was logged
        assert result.exit_code == 0
        assert 'Failed to generate seed data for schema' in result.output


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_view_only_tables(
    runner,
    mock_setup_database_connection,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with view-only tables (no seed data possible)."""
    with patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct:
        # Create mock view-only tables
        mock_tables = {
            'public': [
                TableInfo(name='user_view', schema='public', table_type='VIEW'),
                TableInfo(name='post_view', schema='public', table_type='VIEW'),
            ]
        }
        mock_construct.return_value = mock_tables

        with patch('supabase_pydantic.cli.commands.gen.generate_seed_data') as mock_generate:
            # Return empty seed data
            mock_generate.return_value = {}

            # Run the command
            result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--seed'])

            # Check that the command was successful but with appropriate messages
            assert result.exit_code == 0
            assert 'Failed to generate seed data for schema' in result.output
            assert 'All entities are views in this schema' in result.output


@pytest.mark.unit
@pytest.mark.cli
def test_gen_without_connection_source(runner):
    """Test gen command without any connection source."""
    # Run the command without local or db_url
    # Note: Click will return exit code 2 for missing required parameters
    # even though we have a custom error message in the function
    result = runner.invoke(gen, [])

    # Command should exit with code 2 (CLI argument validation error)
    assert result.exit_code == 2
    # Error message should mention missing mutually exclusive options
    assert 'Missing one of the required mutually exclusive options' in result.output


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_connection_error(runner):
    """Test gen command with a connection error."""
    with patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup:
        # Simulate a connection error
        mock_setup.side_effect = Exception('Failed to connect to database')

        # Run the command
        result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb'])

        # Command should complete but log an error
        assert result.exit_code == 0
        assert 'Error setting up database connection' in result.output


@pytest.mark.unit
@pytest.mark.cli
def test_gen_mysql_schema_handling(runner):
    """Test MySQL schema handling in gen command."""
    with patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup:
        # Configure the mock to return MySQL params
        mock_mysql_params = Mock(spec=MySQLConnectionParams)
        mock_mysql_params.db_url = 'mysql://user:pass@localhost/testdb'
        mock_mysql_params.dbname = None  # Simulate missing dbname
        mock_mysql_params.to_dict.return_value = {'db_url': 'mysql://user:pass@localhost/testdb'}

        mock_setup.return_value = (mock_mysql_params, DatabaseType.MYSQL)

        with patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct:
            # Mock tables with a single schema that doesn't match 'public'
            mock_tables = {'testdb': [TableInfo(name='users', schema='testdb', table_type='BASE TABLE')]}
            mock_construct.return_value = mock_tables

            # Mock get_working_directories
            with patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs:
                mock_dirs.return_value = {'default': '/path/to/dir'}

                # Mock get_standard_jobs
                with patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs:
                    mock_config = Mock()
                    mock_config.enabled = True
                    mock_config.fpath.return_value = '/path/to/dir/model.py'
                    mock_config.file_type = 'pydantic'
                    mock_config.framework_type = None

                    # Set up jobs for 'testdb' schema to match what we're mocking
                    mock_jobs.return_value = {'testdb': {'pydantic_models': mock_config}}

                    # Mock urlparse to return expected values for MySQL URL
                    with patch('supabase_pydantic.cli.commands.gen.urlparse') as mock_urlparse:
                        mock_parsed_url = Mock()
                        mock_parsed_url.path = '/testdb'
                        mock_urlparse.return_value = mock_parsed_url

                        # Mock the FileWriterFactory
                        with patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory:
                            mock_writer = Mock()
                            mock_writer.save.return_value = ('/path/to/model.py', None)
                            mock_factory.return_value.get_file_writer.return_value = mock_writer

                            # Mock the formatter to avoid errors
                            with patch('supabase_pydantic.cli.commands.gen.format_with_ruff'):
                                # Run the command
                                result = runner.invoke(gen, ['--db-url', 'mysql://user:pass@localhost/testdb'])

                                # Check that the command was successful
                                assert result.exit_code == 0

                                # Use a more generic assertion that just checks the schemas parameter
                                # This avoids issues with other parameters that might change
                                _, kwargs = mock_construct.call_args
                                assert kwargs.get('schemas') == ('testdb',), (
                                    "Expected schemas=('testdb',) in construct_tables call"
                                )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_disable_model_prefix_protection(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with disable_model_prefix_protection flag."""
    # Run the command
    result = runner.invoke(
        gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--disable-model-prefix-protection']
    )

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify construct_tables was called with disable_model_prefix_protection=True
    mock_construct_tables.assert_called_once_with(
        conn_type=ANY, db_type=ANY, schemas=ANY, disable_model_prefix_protection=True, connection_params=ANY
    )

    # Verify file writer factory was called with disable_model_prefix_protection=True
    mock_file_writer_factory.get_file_writer.assert_called_with(
        ANY,
        ANY,
        ANY,
        ANY,
        add_null_parent_classes=False,
        database_type=DatabaseType.POSTGRES,
        generate_crud_models=True,
        generate_enums=True,
        disable_model_prefix_protection=True,
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_custom_directory(
    runner, mock_setup_database_connection, mock_construct_tables, mock_get_standard_jobs, mock_file_writer_factory
):
    """Test gen command with custom output directory."""
    with patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs:
        mock_dirs.return_value = {'default': '/custom/path', 'fastapi': '/custom/path/fastapi'}

        # Run the command
        result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--dir', '/custom/path'])

        # Check that the command was successful
        assert result.exit_code == 0

        # Verify get_working_directories was called with the custom directory
        mock_dirs.assert_called_once_with('/custom/path', ANY, auto_create=True)


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_no_overwrite(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with no overwrite flag."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--no-overwrite'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify file writer save was called with overwrite=False
    writer = mock_file_writer_factory.get_file_writer.return_value
    writer.save.assert_called_once_with(False)


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_null_parent_classes(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with null_parent_classes flag."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--null-parent-classes'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify file writer factory was called with add_null_parent_classes=True
    mock_file_writer_factory.get_file_writer.assert_called_with(
        ANY,
        ANY,
        ANY,
        ANY,
        add_null_parent_classes=True,
        database_type=DatabaseType.POSTGRES,
        generate_crud_models=True,
        generate_enums=True,
        disable_model_prefix_protection=False,
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_no_crud_models(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with no_crud_models flag."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--no-crud-models'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify file writer factory was called with generate_crud_models=False
    mock_file_writer_factory.get_file_writer.assert_called_with(
        ANY,
        ANY,
        ANY,
        ANY,
        add_null_parent_classes=False,
        database_type=DatabaseType.POSTGRES,
        generate_crud_models=False,
        generate_enums=True,
        disable_model_prefix_protection=False,
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_no_enums(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with no_enums flag."""
    # Run the command
    result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb', '--no-enums'])

    # Check that the command was successful
    assert result.exit_code == 0

    # Verify file writer factory was called with generate_enums=False
    mock_file_writer_factory.get_file_writer.assert_called_with(
        ANY,
        ANY,
        ANY,
        ANY,
        add_null_parent_classes=False,
        database_type=DatabaseType.POSTGRES,
        generate_crud_models=True,
        generate_enums=False,
        disable_model_prefix_protection=False,
    )


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_ruff_not_found(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command when ruff formatter is not found."""
    from supabase_pydantic.utils.formatting import RuffNotFoundError

    with patch('supabase_pydantic.cli.commands.gen.format_with_ruff') as mock_format:
        # Simulate ruff not found
        mock_format.side_effect = RuffNotFoundError('Ruff not found. Please install ruff.')

        # Run the command
        result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb'])

        # Check that the command was successful but warning was logged
        assert result.exit_code == 0
        assert mock_format.called


@pytest.mark.unit
@pytest.mark.cli
def test_gen_with_formatting_error(
    runner,
    mock_setup_database_connection,
    mock_construct_tables,
    mock_get_working_directories,
    mock_get_standard_jobs,
    mock_file_writer_factory,
):
    """Test gen command with a formatting error."""
    with patch('supabase_pydantic.cli.commands.gen.format_with_ruff') as mock_format:
        # Simulate a generic formatting error
        mock_format.side_effect = Exception('Formatting failed')

        # Run the command
        result = runner.invoke(gen, ['--db-url', 'postgresql://user:pass@localhost/testdb'])

        # Check that the command was successful but error was logged
        assert result.exit_code == 0
        assert mock_format.called


@pytest.mark.unit
@pytest.mark.cli
def test_gen_mysql_schema_fallback_public(runner):
    """Test MySQL schema fallback to 'public' when schema not found."""
    with patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup:
        # Configure the mock to return MySQL params
        mock_mysql_params = Mock(spec=MySQLConnectionParams)
        mock_mysql_params.db_url = 'mysql://user:pass@localhost/testdb'
        mock_mysql_params.dbname = 'testdb'
        mock_mysql_params.to_dict.return_value = {'db_url': 'mysql://user:pass@localhost/testdb'}

        mock_setup.return_value = (mock_mysql_params, DatabaseType.MYSQL)

        with patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct:
            # Mock tables with only 'public' schema available but jobs for 'testdb'
            mock_tables = {'public': [TableInfo(name='users', schema='public', table_type='BASE TABLE')]}
            mock_construct.return_value = mock_tables

            # Mock get_working_directories
            with patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs:
                mock_dirs.return_value = {'default': '/path/to/dir'}

                with patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs:
                    mock_config = Mock()
                    mock_config.enabled = True
                    mock_config.fpath.return_value = '/path/to/entities/model.py'
                    # Use 'pydantic' instead of 'python' for file_type as that's the expected value
                    mock_config.file_type = 'pydantic'
                    # Use None for framework_type as that's the default when not specified
                    mock_config.framework_type = None

                    # Jobs for 'testdb' but tables only available in 'public'
                    mock_jobs.return_value = {'testdb': {'pydantic_models': mock_config}}

                    # Mock the FileWriterFactory
                    with patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory:
                        mock_writer = Mock()
                        mock_writer.save.return_value = ('/path/to/entities/model.py', None)
                        mock_factory.return_value.get_file_writer.return_value = mock_writer

                        # Mock the formatter to avoid errors
                        with patch('supabase_pydantic.cli.commands.gen.format_with_ruff'):
                            # Run the command
                            result = runner.invoke(gen, ['--db-url', 'mysql://user:pass@localhost/testdb'])

                            # Check that the command was successful
                            assert result.exit_code == 0


@pytest.mark.unit
@pytest.mark.cli
def test_gen_mysql_schema_fallback_single_schema(runner):
    """Test MySQL schema fallback to the only available schema."""
    with patch('supabase_pydantic.cli.commands.gen.setup_database_connection') as mock_setup:
        # Configure the mock to return MySQL params
        mock_mysql_params = Mock(spec=MySQLConnectionParams)
        mock_mysql_params.db_url = 'mysql://user:pass@localhost/testdb'
        mock_mysql_params.dbname = 'other_db'  # Mismatch with the actual schema
        mock_mysql_params.to_dict.return_value = {'db_url': 'mysql://user:pass@localhost/testdb'}

        mock_setup.return_value = (mock_mysql_params, DatabaseType.MYSQL)

        with patch('supabase_pydantic.cli.commands.gen.construct_tables') as mock_construct:
            # Only one schema is available, but doesn't match what's in the job
            mock_tables = {'actual_db': [TableInfo(name='users', schema='actual_db', table_type='BASE TABLE')]}
            mock_construct.return_value = mock_tables

            with patch('supabase_pydantic.cli.commands.gen.get_standard_jobs') as mock_jobs:
                mock_config = Mock()
                mock_config.enabled = True
                mock_config.fpath.return_value = '/path/to/entities/model.py'
                mock_config.file_type = 'python'
                mock_config.framework_type = 'fastapi'

                # Jobs for a schema that doesn't match the only available one
                mock_jobs.return_value = {'other_db': {'pydantic_models': mock_config}}

                # Mock get_working_directories
                with patch('supabase_pydantic.cli.commands.gen.get_working_directories') as mock_dirs:
                    mock_dirs.return_value = {'default': '/path/to/dir'}

                    # Mock the FileWriterFactory
                    with patch('supabase_pydantic.cli.commands.gen.FileWriterFactory') as mock_factory:
                        mock_writer = Mock()
                        mock_writer.save.return_value = ('/path/to/model.py', None)
                        mock_factory.return_value.get_file_writer.return_value = mock_writer

                        # Mock the formatter to avoid errors
                        with patch('supabase_pydantic.cli.commands.gen.format_with_ruff'):
                            # Run the command
                            result = runner.invoke(gen, ['--db-url', 'mysql://user:pass@localhost/testdb'])

                            # Check that the command was successful
                            assert result.exit_code == 0
