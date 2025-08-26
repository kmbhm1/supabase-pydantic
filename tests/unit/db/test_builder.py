"""Tests for database builder module."""

import logging
import pytest
from unittest.mock import patch, Mock, MagicMock

from supabase_pydantic.db.builder import DatabaseBuilder, construct_tables
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import TableInfo


@pytest.fixture
def mock_factory():
    """Fixture for mocking DatabaseFactory."""
    with patch('supabase_pydantic.db.builder.DatabaseFactory') as mock_factory_class:
        mock_factory_instance = Mock()
        mock_factory_class.return_value = mock_factory_instance

        # Mock factory components
        mock_connector = Mock()
        mock_connector.__enter__ = Mock()
        mock_connector.__exit__ = Mock(return_value=None)  # Add exit method to properly handle context manager
        mock_reader = Mock()
        mock_marshaler = Mock()

        # Setup factory return values
        mock_factory_instance.create_connector.return_value = mock_connector
        mock_factory_instance.create_schema_reader.return_value = mock_reader
        mock_factory_instance.create_marshalers.return_value = mock_marshaler

        yield {
            'factory_class': mock_factory_class,
            'factory_instance': mock_factory_instance,
            'connector': mock_connector,
            'reader': mock_reader,
            'marshaler': mock_marshaler,
        }


@pytest.fixture
def mock_registrations():
    """Fixture for mocking component registration."""
    with patch('supabase_pydantic.db.builder.register_database_components') as mock_register:
        yield mock_register


@pytest.mark.unit
@pytest.mark.db
def test_database_builder_init(mock_factory, mock_registrations):
    """Test DatabaseBuilder initialization."""
    # Test initialization
    builder = DatabaseBuilder(
        db_type=DatabaseType.POSTGRES,
        conn_type=DatabaseConnectionType.DB_URL,
        connection_params={'db_url': 'postgresql://user:pass@localhost:5432/db'},
    )

    # Verify component registration
    mock_registrations.assert_called_once()

    # Verify factory creates components with correct parameters
    mock_factory['factory_instance'].create_connector.assert_called_once_with(
        DatabaseType.POSTGRES, connection_params={'db_url': 'postgresql://user:pass@localhost:5432/db'}
    )

    mock_factory['factory_instance'].create_schema_reader.assert_called_once_with(
        DatabaseType.POSTGRES, connector=mock_factory['connector']
    )

    mock_factory['factory_instance'].create_marshalers.assert_called_once_with(DatabaseType.POSTGRES)

    # Verify builder has correct components
    assert builder.connector == mock_factory['connector']
    assert builder.schema_reader == mock_factory['reader']
    assert builder.marshaler == mock_factory['marshaler']
    assert builder.db_type == DatabaseType.POSTGRES
    assert builder.conn_type == DatabaseConnectionType.DB_URL


@pytest.mark.unit
@pytest.mark.db
def test_database_builder_init_with_additional_kwargs(mock_factory, mock_registrations):
    """Test DatabaseBuilder initialization with additional kwargs."""
    # Test initialization with additional kwargs
    _ = DatabaseBuilder(
        db_type=DatabaseType.MYSQL,
        conn_type=DatabaseConnectionType.LOCAL,
        connection_params={'db_url': 'mysql://user:pass@localhost:3306/db'},
        socket='/tmp/mysql.sock',
        ssl_mode='required',
    )

    # Verify component registration
    mock_registrations.assert_called_once()

    # Verify factory creates components with correct parameters
    mock_factory['factory_instance'].create_connector.assert_called_once_with(
        DatabaseType.MYSQL,
        connection_params={'db_url': 'mysql://user:pass@localhost:3306/db'},
        socket='/tmp/mysql.sock',
        ssl_mode='required',
    )


@pytest.mark.unit
@pytest.mark.db
def test_build_tables(mock_factory):
    """Test building tables from database."""
    # Setup connection and reader mock returns
    mock_connection = Mock()
    mock_factory['connector'].__enter__.return_value = mock_connection
    mock_factory['connector'].check_connection.return_value = True

    # Mock schema reader return values
    mock_factory['reader'].get_schemas.return_value = ['public', 'other']
    mock_factory['reader'].get_tables.return_value = [('public', 'users', 'BASE TABLE')]
    mock_factory['reader'].get_columns.return_value = [
        ('public', 'users', 'BASE TABLE', 'id', 'integer', 'NO', None, True, 'int4', 'pg_catalog', 'int4', True)
    ]
    mock_factory['reader'].get_constraints.return_value = [('public', 'users', 'pk_users', 'p', 'PRIMARY KEY (id)')]
    mock_factory['reader'].get_foreign_keys.return_value = []
    mock_factory['reader'].get_user_defined_types.return_value = []
    mock_factory['reader'].get_type_mappings.return_value = []

    # Mock marshaler return value
    mock_table_info = [TableInfo(name='users', schema='public', table_type='BASE TABLE')]
    mock_factory['marshaler'].construct_table_info.return_value = mock_table_info

    # Create builder
    builder = DatabaseBuilder(db_type=DatabaseType.POSTGRES, conn_type=DatabaseConnectionType.DB_URL)

    # Call build_tables
    result = builder.build_tables(schemas=('public',))

    # Verify connection was established and checked
    mock_factory['connector'].__enter__.assert_called_once()
    mock_factory['connector'].__exit__.assert_called_once()  # Verify exit method was called
    mock_factory['connector'].check_connection.assert_called_once_with(mock_connection)

    # Verify schema reader methods were called
    mock_factory['reader'].get_schemas.assert_called_once_with(mock_connection)
    mock_factory['reader'].get_tables.assert_called_once_with(mock_connection, 'public')
    mock_factory['reader'].get_columns.assert_called_once_with(mock_connection, 'public')
    mock_factory['reader'].get_constraints.assert_called_once_with(mock_connection, 'public')
    mock_factory['reader'].get_foreign_keys.assert_called_once_with(mock_connection, 'public')
    mock_factory['reader'].get_user_defined_types.assert_called_once_with(mock_connection, 'public')
    mock_factory['reader'].get_type_mappings.assert_called_once_with(mock_connection, 'public')

    # Verify marshaler was called with the right parameters
    mock_factory['marshaler'].construct_table_info.assert_called_once_with(
        table_data=[('public', 'users', 'BASE TABLE')],
        column_data=[
            ('public', 'users', 'BASE TABLE', 'id', 'integer', 'NO', None, True, 'int4', 'pg_catalog', 'int4', True)
        ],
        fk_data=[],
        constraint_data=[('public', 'users', 'pk_users', 'p', 'PRIMARY KEY (id)')],
        type_data=[],
        type_mapping_data=[],
        schema='public',
        disable_model_prefix_protection=False,
    )

    # Verify result
    assert result == {'public': mock_table_info}


@pytest.mark.unit
@pytest.mark.db
def test_build_tables_with_multiple_schemas(mock_factory):
    """Test building tables from multiple schemas."""
    # Setup connection and reader mock returns
    mock_connection = Mock()
    mock_factory['connector'].__enter__.return_value = mock_connection
    mock_factory['connector'].check_connection.return_value = True

    # Mock schema reader return values
    mock_factory['reader'].get_schemas.return_value = ['public', 'auth', 'other']

    # Mock marshaler return values
    public_tables = [TableInfo(name='users', schema='public', table_type='BASE TABLE')]
    auth_tables = [TableInfo(name='users', schema='auth', table_type='BASE TABLE')]

    def mock_construct_table_info(**kwargs):
        schema = kwargs['schema']
        if schema == 'public':
            return public_tables
        elif schema == 'auth':
            return auth_tables
        return []

    mock_factory['marshaler'].construct_table_info.side_effect = mock_construct_table_info

    # Create builder
    builder = DatabaseBuilder(db_type=DatabaseType.POSTGRES, conn_type=DatabaseConnectionType.DB_URL)

    # Call build_tables with multiple schemas
    result = builder.build_tables(schemas=('public', 'auth'))

    # Verify schemas were processed
    assert mock_factory['reader'].get_tables.call_count == 2
    assert mock_factory['marshaler'].construct_table_info.call_count == 2

    # Verify result includes both schemas
    assert result == {'public': public_tables, 'auth': auth_tables}


@pytest.mark.unit
@pytest.mark.db
def test_build_tables_with_wildcard_schema(mock_factory):
    """Test building tables using wildcard schema selector."""
    # Setup connection and reader mock returns
    mock_connection = Mock()
    mock_factory['connector'].__enter__.return_value = mock_connection
    mock_factory['connector'].check_connection.return_value = True

    # Mock schema reader return values
    mock_factory['reader'].get_schemas.return_value = ['public', 'auth', 'other']

    # Mock marshaler return values
    tables_by_schema = {
        'public': [TableInfo(name='users', schema='public', table_type='BASE TABLE')],
        'auth': [TableInfo(name='roles', schema='auth', table_type='BASE TABLE')],
        'other': [TableInfo(name='logs', schema='other', table_type='BASE TABLE')],
    }

    def mock_construct_table_info(**kwargs):
        schema = kwargs['schema']
        return tables_by_schema.get(schema, [])

    mock_factory['marshaler'].construct_table_info.side_effect = mock_construct_table_info

    # Create builder
    builder = DatabaseBuilder(db_type=DatabaseType.POSTGRES, conn_type=DatabaseConnectionType.DB_URL)

    # Call build_tables with wildcard schema
    result = builder.build_tables(schemas=('*',))

    # Verify all schemas were processed
    assert mock_factory['reader'].get_tables.call_count == 3
    assert mock_factory['marshaler'].construct_table_info.call_count == 3

    # Verify result includes all schemas
    assert result == tables_by_schema


@pytest.mark.unit
@pytest.mark.db
def test_build_tables_connection_error(mock_factory):
    """Test handling connection error in build_tables in both normal and debug modes."""
    # Setup connection error
    mock_connection = Mock()
    mock_factory['connector'].__enter__.return_value = mock_connection
    mock_factory['connector'].check_connection.return_value = False

    # Create builder
    builder = DatabaseBuilder(db_type=DatabaseType.POSTGRES, conn_type=DatabaseConnectionType.DB_URL)

    # 1. Test normal mode - should not raise ConnectionError
    # Just log the error
    try:
        builder.build_tables()
    except ConnectionError:
        pytest.fail('ConnectionError should not be raised in normal mode')

    # 2. Test debug mode - should raise ConnectionError
    # Set logger level to DEBUG by patching the getEffectiveLevel method
    with patch('supabase_pydantic.db.builder.logger.getEffectiveLevel', return_value=logging.DEBUG):
        # Call build_tables and expect ConnectionError
        with pytest.raises(ConnectionError) as exc_info:
            builder.build_tables()

        assert 'Failed to establish database connection' in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.db
def test_construct_tables_with_connection_params():
    """Test construct_tables function with connection params."""
    # Setup mocks
    mock_builder_class = Mock()
    mock_builder_instance = Mock()
    mock_builder_class.return_value = mock_builder_instance

    mock_tables = {'public': [TableInfo(name='users', schema='public', table_type='BASE TABLE')]}
    mock_builder_instance.build_tables.return_value = mock_tables

    connection_params = {'db_url': 'postgresql://user:pass@localhost:5432/db'}

    # Patch the DatabaseBuilder class
    with patch('supabase_pydantic.db.builder.DatabaseBuilder', mock_builder_class):
        # Call construct_tables
        result = construct_tables(
            conn_type=DatabaseConnectionType.DB_URL,
            db_type=DatabaseType.POSTGRES,
            schemas=('public',),
            disable_model_prefix_protection=True,
            connection_params=connection_params,
        )

        # Verify DatabaseBuilder was initialized correctly
        mock_builder_class.assert_called_once_with(
            DatabaseType.POSTGRES, DatabaseConnectionType.DB_URL, connection_params=connection_params
        )

        # Verify build_tables was called with correct parameters
        mock_builder_instance.build_tables.assert_called_once_with(
            schemas=('public',), disable_model_prefix_protection=True
        )

        # Verify result
        assert result == mock_tables


@pytest.mark.unit
@pytest.mark.db
def test_construct_tables_with_kwargs():
    """Test construct_tables function with kwargs."""
    # Setup mocks
    mock_builder_class = Mock()
    mock_builder_instance = Mock()
    mock_builder_class.return_value = mock_builder_instance

    mock_tables = {'public': [TableInfo(name='users', schema='public', table_type='BASE TABLE')]}
    mock_builder_instance.build_tables.return_value = mock_tables

    # Patch the DatabaseBuilder class
    with patch('supabase_pydantic.db.builder.DatabaseBuilder', mock_builder_class):
        # Call construct_tables with kwargs but no connection_params
        result = construct_tables(
            conn_type=DatabaseConnectionType.LOCAL,
            db_type=DatabaseType.MYSQL,
            schemas=('public',),
            disable_model_prefix_protection=False,
            host='localhost',
            port='3306',
            user='testuser',
            password='testpass',
            dbname='testdb',
        )

        # Verify DatabaseBuilder was initialized correctly
        mock_builder_class.assert_called_once_with(
            DatabaseType.MYSQL,
            DatabaseConnectionType.LOCAL,
            host='localhost',
            port='3306',
            user='testuser',
            password='testpass',
            dbname='testdb',
        )

        # Verify build_tables was called with correct parameters
        mock_builder_instance.build_tables.assert_called_once_with(
            schemas=('public',), disable_model_prefix_protection=False
        )

        # Verify result
        assert result == mock_tables


@pytest.mark.unit
@pytest.mark.db
def test_database_builder_integration():
    """Test DatabaseBuilder integration with mocked components."""
    # Define mock database components
    mock_connector = MagicMock()
    mock_connector.__enter__ = Mock()
    mock_connector.__exit__ = Mock(return_value=None)  # Add exit method to properly handle context manager
    mock_reader = MagicMock()
    mock_marshaler = MagicMock()

    # Setup connection mock
    mock_connection = Mock()
    mock_connector.__enter__.return_value = mock_connection
    mock_connector.check_connection.return_value = True

    # Setup reader mock
    mock_reader.get_schemas.return_value = ['public']
    mock_reader.get_tables.return_value = [('public', 'users', 'BASE TABLE')]
    mock_reader.get_columns.return_value = [
        ('public', 'users', 'BASE TABLE', 'id', 'integer', 'NO', None, True, 'int4', 'pg_catalog', 'int4', True)
    ]
    mock_reader.get_constraints.return_value = []
    mock_reader.get_foreign_keys.return_value = []
    mock_reader.get_user_defined_types.return_value = []
    mock_reader.get_type_mappings.return_value = []

    # Setup marshaler mock
    mock_table_info = [TableInfo(name='users', schema='public', table_type='BASE TABLE')]
    mock_marshaler.construct_table_info.return_value = mock_table_info

    # Create factory mock that returns our component mocks
    mock_factory = MagicMock()
    mock_factory.create_connector.return_value = mock_connector
    mock_factory.create_schema_reader.return_value = mock_reader
    mock_factory.create_marshalers.return_value = mock_marshaler

    # Patch factory class and component registration
    with (
        patch('supabase_pydantic.db.builder.DatabaseFactory', return_value=mock_factory),
        patch('supabase_pydantic.db.builder.register_database_components'),
    ):
        # Create DatabaseBuilder
        builder = DatabaseBuilder(
            db_type=DatabaseType.POSTGRES,
            conn_type=DatabaseConnectionType.DB_URL,
            db_url='postgresql://user:pass@localhost:5432/db',
        )

        # Build tables
        tables = builder.build_tables()

        # Verify expected behavior
        assert tables == {'public': mock_table_info}
        mock_connector.__enter__.assert_called_once()
        mock_connector.__exit__.assert_called_once()  # Verify exit method was called
        mock_reader.get_schemas.assert_called_once_with(mock_connection)
        mock_marshaler.construct_table_info.assert_called_once()
