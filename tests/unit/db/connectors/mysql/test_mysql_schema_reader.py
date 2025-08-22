"""Tests for MySQL schema reader implementation."""

from unittest.mock import MagicMock, patch

import pytest

from supabase_pydantic.db.connectors.mysql.connector import MySQLConnector
from supabase_pydantic.db.connectors.mysql.schema_reader import MySQLSchemaReader


@pytest.fixture
def mock_mysql_connection():
    """Mock MySQL connection with dictionary cursor support."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Configure cursor to return dictionary results by default
    def dict_cursor(**kwargs):
        # Ensure the dictionary=True parameter works
        if kwargs.get('dictionary', False):
            mock_cursor.description = [('column1',), ('column2',)]
        return mock_cursor

    mock_conn.cursor = MagicMock(side_effect=dict_cursor)

    return mock_conn, mock_cursor


@pytest.fixture
def schema_reader():
    """Create a MySQLSchemaReader with a mock connector."""
    mock_connector = MagicMock(spec=MySQLConnector)
    return MySQLSchemaReader(connector=mock_connector)


@pytest.mark.unit
@pytest.mark.db
class TestMySQLSchemaReader:
    """Test cases for the MySQL schema reader implementation."""

    def test_execute_query_without_params(self, schema_reader, mock_mysql_connection):
        """Test executing a query without parameters."""
        mock_conn, mock_cursor = mock_mysql_connection

        # Set up mock cursor to return specific results
        expected_results = [{'id': 1, 'name': 'Row 1'}, {'id': 2, 'name': 'Row 2'}]
        mock_cursor.fetchall.return_value = expected_results

        # Execute query without parameters
        query = 'SELECT * FROM test_table'
        results = schema_reader.execute_query(mock_conn, query)

        # Verify query execution
        mock_cursor.execute.assert_called_once_with(query)
        mock_cursor.fetchall.assert_called_once()

        # Verify results are returned correctly
        assert results == expected_results

        # Verify cursor was properly created and closed
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_query_with_params(self, schema_reader, mock_mysql_connection):
        """Test executing a query with parameters."""
        mock_conn, mock_cursor = mock_mysql_connection

        # Set up mock cursor to return results
        expected_results = [{'id': 1, 'name': 'Test'}]
        mock_cursor.fetchall.return_value = expected_results

        # Execute query with parameters
        query = 'SELECT * FROM test_table WHERE schema = %s'
        params = {'schema': 'testdb'}
        results = schema_reader.execute_query(mock_conn, query, params)

        # Verify query execution with tuple parameters
        mock_cursor.execute.assert_called_once_with(query, tuple(params.values()))
        mock_cursor.fetchall.assert_called_once()

        # Verify results are returned correctly
        assert results == expected_results

    def test_execute_query_handles_exception(self, schema_reader, mock_mysql_connection):
        """Test that execute_query properly handles and re-raises exceptions."""
        mock_conn, mock_cursor = mock_mysql_connection

        # Configure cursor to raise an exception
        error_message = 'Query execution failed'
        mock_cursor.execute.side_effect = Exception(error_message)

        # Test exception handling
        query = 'SELECT * FROM non_existent_table'
        with pytest.raises(Exception) as exc_info:
            schema_reader.execute_query(mock_conn, query)

        assert str(exc_info.value) == error_message

        # Verify cursor was created and closed even with error
        mock_conn.cursor.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_parse_mysql_enum_values_empty(self, schema_reader):
        """Test parsing empty enum values string."""
        assert schema_reader.parse_mysql_enum_values('') == []

    def test_parse_mysql_enum_values_simple(self, schema_reader):
        """Test parsing simple enum values."""
        enum_string = "'value1','value2','value3'"
        expected = ['value1', 'value2', 'value3']
        assert schema_reader.parse_mysql_enum_values(enum_string) == expected

    def test_parse_mysql_enum_values_with_special_chars(self, schema_reader):
        """Test parsing enum values with special characters."""
        enum_string = "'value,1','value\\'2','value''3'"
        expected = ['value,1', "value'2", "value'3"]
        assert schema_reader.parse_mysql_enum_values(enum_string) == expected

    def test_get_schemas(self, schema_reader, mock_mysql_connection):
        """Test retrieving database schemas."""
        mock_conn, mock_cursor = mock_mysql_connection

        # Mock the execute_query method to return specific results
        schema_data = [{'SCHEMA_NAME': 'schema1'}, {'SCHEMA_NAME': 'schema2'}]

        with patch.object(schema_reader, 'execute_query', return_value=schema_data):
            schemas = schema_reader.get_schemas(mock_conn)

            assert schemas == ['schema1', 'schema2']

    def test_get_schemas_empty_result(self, schema_reader, mock_mysql_connection):
        """Test retrieving schemas when there are no results."""
        mock_conn, mock_cursor = mock_mysql_connection

        # Mock execute_query to return empty list
        with patch.object(schema_reader, 'execute_query', return_value=[]):
            schemas = schema_reader.get_schemas(mock_conn)

            assert schemas == []

    def test_get_schemas_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_schemas handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            schemas = schema_reader.get_schemas(mock_conn)

            # Should return empty list on exception
            assert schemas == []

    def test_get_tables(self, schema_reader, mock_mysql_connection):
        """Test retrieving tables from a schema."""
        mock_conn, _ = mock_mysql_connection

        # Mock the execute_query method to return specific results
        table_data = [
            {'table_name': 'table1', 'table_type': 'BASE TABLE'},
            {'table_name': 'table2', 'table_type': 'BASE TABLE'},
        ]

        with patch.object(schema_reader, 'execute_query', return_value=table_data):
            tables = schema_reader.get_tables(mock_conn, 'testschema')

            assert len(tables) == 2
            assert tables[0]['table_name'] == 'table1'
            assert tables[1]['table_name'] == 'table2'

    def test_get_tables_empty_result(self, schema_reader, mock_mysql_connection):
        """Test retrieving tables when there are no results."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to return empty list
        with patch.object(schema_reader, 'execute_query', return_value=[]):
            tables = schema_reader.get_tables(mock_conn, 'testschema')

            assert tables == []

    def test_get_tables_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_tables handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            tables = schema_reader.get_tables(mock_conn, 'testschema')

            # Should return empty list on exception
            assert tables == []

    def test_get_columns_for_all_tables(self, schema_reader, mock_mysql_connection):
        """Test retrieving columns for all tables in a schema."""
        mock_conn, _ = mock_mysql_connection

        # Mock the execute_query method to return specific results
        column_data = [
            {'table_name': 'table1', 'column_name': 'id', 'data_type': 'int'},
            {'table_name': 'table1', 'column_name': 'name', 'data_type': 'varchar'},
            {'table_name': 'table2', 'column_name': 'id', 'data_type': 'int'},
        ]

        with patch.object(schema_reader, 'execute_query', return_value=column_data):
            columns = schema_reader.get_columns(mock_conn, 'testschema')

            assert len(columns) == 3
            assert columns[0]['table_name'] == 'table1'
            assert columns[0]['column_name'] == 'id'

    def test_get_columns_for_specific_table(self, schema_reader, mock_mysql_connection):
        """Test retrieving columns for a specific table."""
        mock_conn, _ = mock_mysql_connection

        # Mock the execute_query method to return specific results
        column_data = [
            {'table_name': 'table1', 'column_name': 'id', 'data_type': 'int'},
            {'table_name': 'table1', 'column_name': 'name', 'data_type': 'varchar'},
        ]

        with patch.object(schema_reader, 'execute_query', return_value=column_data):
            columns = schema_reader.get_columns(mock_conn, 'testschema', 'table1')

            assert len(columns) == 2
            assert columns[0]['table_name'] == 'table1'
            assert columns[1]['column_name'] == 'name'

    def test_get_columns_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_columns handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            columns = schema_reader.get_columns(mock_conn, 'testschema')

            # Should return empty list on exception
            assert columns == []

    def test_get_constraints(self, schema_reader, mock_mysql_connection):
        """Test retrieving constraints from a schema."""
        mock_conn, _ = mock_mysql_connection

        # Mock the execute_query method to return specific results
        constraint_data = [
            {'table_name': 'table1', 'constraint_name': 'pk_table1', 'constraint_type': 'PRIMARY KEY'},
            {'table_name': 'table1', 'constraint_name': 'unique_name', 'constraint_type': 'UNIQUE'},
        ]

        with patch.object(schema_reader, 'execute_query', return_value=constraint_data):
            constraints = schema_reader.get_constraints(mock_conn, 'testschema')

            assert len(constraints) == 2
            assert constraints[0]['constraint_name'] == 'pk_table1'
            assert constraints[1]['constraint_type'] == 'UNIQUE'

    def test_get_constraints_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_constraints handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            constraints = schema_reader.get_constraints(mock_conn, 'testschema')

            # Should return empty list on exception
            assert constraints == []

    def test_get_foreign_keys(self, schema_reader, mock_mysql_connection):
        """Test retrieving foreign keys from a schema."""
        mock_conn, _ = mock_mysql_connection

        # Mock the execute_query method to return specific results
        fk_data = [
            {
                'constraint_name': 'fk_posts_user',
                'source_table': 'posts',
                'source_column': 'user_id',
                'target_table': 'users',
                'target_column': 'id',
            },
            {
                'constraint_name': 'fk_comments_post',
                'source_table': 'comments',
                'source_column': 'post_id',
                'target_table': 'posts',
                'target_column': 'id',
            },
        ]

        with patch.object(schema_reader, 'execute_query', return_value=fk_data):
            foreign_keys = schema_reader.get_foreign_keys(mock_conn, 'testschema')

            assert len(foreign_keys) == 2
            assert foreign_keys[0]['constraint_name'] == 'fk_posts_user'
            assert foreign_keys[1]['source_table'] == 'comments'

    def test_get_foreign_keys_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_foreign_keys handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            foreign_keys = schema_reader.get_foreign_keys(mock_conn, 'testschema')

            # Should return empty list on exception
            assert foreign_keys == []

    def test_get_user_defined_types(self, schema_reader, mock_mysql_connection):
        """Test retrieving user-defined types (enums) from a schema."""
        mock_conn, _ = mock_mysql_connection

        # Raw enum data from database
        enum_data = [
            {
                'table_name': 'users',
                'column_name': 'status',
                'data_type': 'enum',
                'enum_values': "'active','inactive','pending'",
            },
            {
                'table_name': 'posts',
                'column_name': 'visibility',
                'data_type': 'enum',
                'enum_values': "'public','private','draft'",
            },
        ]

        # Mock the parse_mysql_enum_values method to properly process enum values
        with patch.object(schema_reader, 'execute_query', return_value=enum_data):
            with patch.object(
                schema_reader,
                'parse_mysql_enum_values',
                side_effect=[['active', 'inactive', 'pending'], ['public', 'private', 'draft']],
            ):
                enums = schema_reader.get_user_defined_types(mock_conn, 'testschema')

                assert len(enums) == 2
                assert enums[0]['enum_values'] == ['active', 'inactive', 'pending']
                assert enums[1]['enum_values'] == ['public', 'private', 'draft']

    def test_get_user_defined_types_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_user_defined_types handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            udts = schema_reader.get_user_defined_types(mock_conn, 'testschema')

            # Should return empty list on exception
            assert udts == []

    def test_get_type_mappings(self, schema_reader, mock_mysql_connection):
        """Test retrieving type mappings from a schema."""
        mock_conn, _ = mock_mysql_connection

        # Mock the execute_query method to return specific results
        type_data = [
            {'type_name': 'int', 'data_type': 'integer'},
            {'type_name': 'varchar', 'data_type': 'character varying'},
        ]

        with patch.object(schema_reader, 'execute_query', return_value=type_data):
            type_mappings = schema_reader.get_type_mappings(mock_conn, 'testschema')

            assert len(type_mappings) == 2
            assert type_mappings[0]['type_name'] == 'int'
            assert type_mappings[1]['data_type'] == 'character varying'

    def test_get_type_mappings_exception_handling(self, schema_reader, mock_mysql_connection):
        """Test that get_type_mappings handles exceptions gracefully."""
        mock_conn, _ = mock_mysql_connection

        # Mock execute_query to raise an exception
        with patch.object(schema_reader, 'execute_query', side_effect=Exception('Query failed')):
            type_mappings = schema_reader.get_type_mappings(mock_conn, 'testschema')

            # Should return empty list on exception
            assert type_mappings == []
