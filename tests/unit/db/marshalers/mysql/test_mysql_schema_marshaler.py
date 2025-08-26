"""Tests for MySQL schema marshaler implementation."""

import pytest
from unittest.mock import patch, MagicMock, call

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.marshalers.mysql.schema import (
    MySQLSchemaMarshaler,
    get_enum_types,
    add_mysql_user_defined_types_to_tables,
)
from supabase_pydantic.db.models import TableInfo, UserEnumType, ColumnInfo


@pytest.fixture
def mock_marshalers():
    """Create mock marshalers for testing."""
    column_marshaler = MagicMock()
    constraint_marshaler = MagicMock()
    relationship_marshaler = MagicMock()

    return {
        'column_marshaler': column_marshaler,
        'constraint_marshaler': constraint_marshaler,
        'relationship_marshaler': relationship_marshaler,
    }


@pytest.fixture
def schema_marshaler(mock_marshalers):
    """Create a MySQLSchemaMarshaler instance for testing."""
    return MySQLSchemaMarshaler(
        column_marshaler=mock_marshalers['column_marshaler'],
        constraint_marshaler=mock_marshalers['constraint_marshaler'],
        relationship_marshaler=mock_marshalers['relationship_marshaler'],
    )


@pytest.fixture
def sample_column_data():
    """Create sample column data for testing."""
    return [
        {
            'TABLE_SCHEMA': 'test_schema',
            'TABLE_NAME': 'users',
            'COLUMN_NAME': 'id',
            'COLUMN_DEFAULT': None,
            'IS_NULLABLE': 'NO',
            'DATA_TYPE': 'int',
            'CHARACTER_MAXIMUM_LENGTH': None,
            'TABLE_TYPE': 'BASE TABLE',
            'IDENTITY_GENERATION': None,
            'UDT_NAME': 'int',
            'ARRAY_ELEMENT_TYPE': None,
        },
        {
            'TABLE_SCHEMA': 'test_schema',
            'TABLE_NAME': 'users',
            'COLUMN_NAME': 'username',
            'COLUMN_DEFAULT': None,
            'IS_NULLABLE': 'YES',
            'DATA_TYPE': 'varchar',
            'CHARACTER_MAXIMUM_LENGTH': 255,
            'TABLE_TYPE': 'BASE TABLE',
            'IDENTITY_GENERATION': None,
            'UDT_NAME': 'varchar',
            'ARRAY_ELEMENT_TYPE': None,
        },
        {
            'TABLE_SCHEMA': 'test_schema',
            'TABLE_NAME': 'posts',
            'COLUMN_NAME': 'id',
            'COLUMN_DEFAULT': None,
            'IS_NULLABLE': 'NO',
            'DATA_TYPE': 'int',
            'CHARACTER_MAXIMUM_LENGTH': None,
            'TABLE_TYPE': 'BASE TABLE',
            'IDENTITY_GENERATION': None,
            'UDT_NAME': 'int',
            'ARRAY_ELEMENT_TYPE': None,
        },
        {
            'TABLE_SCHEMA': 'test_schema',
            'TABLE_NAME': 'posts',
            'COLUMN_NAME': 'user_id',
            'COLUMN_DEFAULT': None,
            'IS_NULLABLE': 'YES',
            'DATA_TYPE': 'int',
            'CHARACTER_MAXIMUM_LENGTH': None,
            'TABLE_TYPE': 'BASE TABLE',
            'IDENTITY_GENERATION': None,
            'UDT_NAME': 'int',
            'ARRAY_ELEMENT_TYPE': None,
        },
    ]


@pytest.fixture
def sample_enum_data():
    """Create sample enum type data for testing."""
    return [
        {
            'type_name': 'status_enum',
            'namespace': 'test_schema',
            'owner': 'admin',
            'category': 'E',
            'is_defined': True,
            'type': 'e',
            'enum_values': ['pending', 'active', 'inactive'],
        },
        {
            'type_name': 'post_status',
            'namespace': 'test_schema',
            'owner': 'admin',
            'category': 'E',
            'is_defined': True,
            'type': 'e',
            'enum_values': ['draft', 'published', 'archived'],
        },
        # A non-enum type
        {
            'type_name': 'some_other_type',
            'namespace': 'test_schema',
            'owner': 'admin',
            'category': 'D',
            'is_defined': True,
            'type': 'd',  # Not an enum
            'enum_values': None,
        },
        # Enum in a different schema
        {
            'type_name': 'other_schema_enum',
            'namespace': 'other_schema',
            'owner': 'admin',
            'category': 'E',
            'is_defined': True,
            'type': 'e',
            'enum_values': ['one', 'two', 'three'],
        },
    ]


@pytest.fixture
def sample_enum_mapping_data():
    """Create sample enum type mapping data for testing."""
    return [
        {
            'column_name': 'status',
            'table_name': 'users',
            'namespace': 'test_schema',
            'type_name': 'status_enum',
            'type_category': 'E',
            'type_description': 'User status enum',
        },
        {
            'column_name': 'status',
            'table_name': 'posts',
            'namespace': 'test_schema',
            'type_name': 'post_status',
            'type_category': 'E',
            'type_description': 'Post status enum',
        },
        # Mapping in a different schema
        {
            'column_name': 'status',
            'table_name': 'other_table',
            'namespace': 'other_schema',
            'type_name': 'other_schema_enum',
            'type_category': 'E',
            'type_description': 'Other enum',
        },
    ]


@pytest.fixture
def sample_tables():
    """Create sample tables for testing."""
    # Create users table
    users_columns = [
        ColumnInfo(
            name='id',
            primary=True,
            is_unique=True,
            is_foreign_key=False,
            post_gres_datatype='int',
            datatype='int',
        ),
        ColumnInfo(
            name='username',
            primary=False,
            is_unique=False,
            is_foreign_key=False,
            post_gres_datatype='varchar',
            datatype='str',
        ),
        ColumnInfo(
            name='status',
            primary=False,
            is_unique=False,
            is_foreign_key=False,
            post_gres_datatype='status_enum',
            datatype='str',
        ),
    ]

    # Create posts table
    posts_columns = [
        ColumnInfo(
            name='id',
            primary=True,
            is_unique=True,
            is_foreign_key=False,
            post_gres_datatype='int',
            datatype='int',
        ),
        ColumnInfo(
            name='user_id',
            primary=False,
            is_unique=False,
            is_foreign_key=True,
            post_gres_datatype='int',
            datatype='int',
        ),
        ColumnInfo(
            name='status',
            primary=False,
            is_unique=False,
            is_foreign_key=False,
            post_gres_datatype='post_status',
            datatype='str',
        ),
        ColumnInfo(
            name='tags',
            primary=False,
            is_unique=False,
            is_foreign_key=False,
            post_gres_datatype='varchar',
            datatype='list[str]',
            array_element_type='varchar',
        ),
    ]

    users_table = TableInfo(
        name='users',
        schema='test_schema',
        table_type='BASE TABLE',
        columns=users_columns,
        constraints=[],
    )

    posts_table = TableInfo(
        name='posts',
        schema='test_schema',
        table_type='BASE TABLE',
        columns=posts_columns,
        constraints=[],
    )

    tables = {
        ('test_schema', 'users'): users_table,
        ('test_schema', 'posts'): posts_table,
    }

    return tables


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_schema_marshaler_initialization(mock_marshalers):
    """Test MySQL schema marshaler initialization."""
    marshaler = MySQLSchemaMarshaler(
        mock_marshalers['column_marshaler'],
        mock_marshalers['constraint_marshaler'],
        mock_marshalers['relationship_marshaler'],
    )

    assert marshaler.column_marshaler == mock_marshalers['column_marshaler']
    assert marshaler.constraint_marshaler == mock_marshalers['constraint_marshaler']
    assert marshaler.relationship_marshaler == mock_marshalers['relationship_marshaler']
    assert marshaler.db_type == DatabaseType.MYSQL


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_columns(schema_marshaler, sample_column_data):
    """Test processing column data."""
    result = schema_marshaler.process_columns(sample_column_data)

    # Verify that we have the correct number of processed columns
    assert len(result) == 4

    # Check the first column's processed data
    first_column = result[0]
    assert first_column[0] == 'test_schema'  # schema
    assert first_column[1] == 'users'  # table_name
    assert first_column[2] == 'id'  # column_name
    assert first_column[5] == 'int'  # data_type

    # Check that all columns are processed
    table_columns = [(col[1], col[2]) for col in result]  # (table_name, column_name)
    assert ('users', 'id') in table_columns
    assert ('users', 'username') in table_columns
    assert ('posts', 'id') in table_columns
    assert ('posts', 'user_id') in table_columns


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_columns_warning_on_missing_data(schema_marshaler):
    """Test that a warning is logged when column data is missing schema/table info."""
    incomplete_data = [
        {'COLUMN_NAME': 'id'},  # Missing TABLE_SCHEMA and TABLE_NAME
    ]

    with patch('supabase_pydantic.db.marshalers.mysql.schema.logger') as mock_logger:
        result = schema_marshaler.process_columns(incomplete_data)

        # The method should log a warning and return an empty list
        assert len(result) == 0
        mock_logger.warning.assert_called_once()
        assert 'missing table_schema and table_name' in mock_logger.warning.call_args[0][0]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_constraints(schema_marshaler):
    """Test processing constraint data."""
    # The MySQL implementation just returns the input data
    constraint_data = [('constraint1',), ('constraint2',)]
    result = schema_marshaler.process_constraints(constraint_data)

    assert result == constraint_data


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_table_details_from_columns(schema_marshaler, sample_column_data):
    """Test getting table details from column data."""
    with patch('supabase_pydantic.db.marshalers.mysql.schema.get_table_details_from_columns') as mock_get_details:
        mock_get_details.return_value = {'mocked': 'result'}

        result = schema_marshaler.get_table_details_from_columns(sample_column_data)

        # Verify the common implementation was called with correct parameters
        mock_get_details.assert_called_once()

        # Check first argument (processed column data)
        processed_column_data = mock_get_details.call_args[0][0]
        assert len(processed_column_data) == 4

        # Check column_marshaler parameter
        assert mock_get_details.call_args[1]['column_marshaler'] == schema_marshaler.column_marshaler

        # Verify the result
        assert result == {'mocked': 'result'}


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_process_foreign_keys(schema_marshaler, sample_tables):
    """Test processing foreign keys."""
    fk_data = [
        ('test_schema', 'posts', 'user_id', 'test_schema', 'users', 'id', 'CASCADE', 'CASCADE'),
    ]

    with patch('supabase_pydantic.db.marshalers.mysql.schema.add_foreign_key_info_to_table_details') as mock_add_fk:
        schema_marshaler.process_foreign_keys(sample_tables, fk_data)

        # Verify the common implementation was called with correct parameters
        mock_add_fk.assert_called_once_with(sample_tables, fk_data)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_construct_table_info(schema_marshaler, sample_column_data, sample_tables):
    """Test constructing table info from database details."""
    # Mock data for test
    table_data = [{'TABLE_NAME': 'users'}, {'TABLE_NAME': 'posts'}]
    column_data = sample_column_data
    fk_data = [('test_schema', 'posts', 'user_id', 'test_schema', 'users', 'id', 'CASCADE', 'CASCADE')]
    constraint_data = [
        ('test_schema', 'users', 'pk_users', 'PRIMARY KEY', 'id'),
        ('test_schema', 'posts', 'pk_posts', 'PRIMARY KEY', 'id'),
    ]
    type_data = [
        {'type_name': 'status_enum', 'namespace': 'test_schema', 'type': 'e', 'enum_values': ['active', 'inactive']},
    ]
    type_mapping_data = [
        {'column_name': 'status', 'table_name': 'users', 'namespace': 'test_schema', 'type_name': 'status_enum'},
    ]
    schema = 'test_schema'

    # Mock all the function calls
    with (
        patch('supabase_pydantic.db.marshalers.mysql.schema.get_table_details_from_columns') as mock_get_details,
        patch('supabase_pydantic.db.marshalers.mysql.schema.add_foreign_key_info_to_table_details') as mock_add_fk,
        patch('supabase_pydantic.db.marshalers.mysql.schema.add_constraints_to_table_details') as mock_add_constraints,
        patch(
            'supabase_pydantic.db.marshalers.mysql.schema.add_relationships_to_table_details'
        ) as mock_add_relationships,
        patch('supabase_pydantic.db.marshalers.mysql.schema.get_enum_types') as mock_get_enum_types,
        patch('supabase_pydantic.db.marshalers.mysql.schema.add_mysql_user_defined_types_to_tables') as mock_add_types,
        patch('supabase_pydantic.db.marshalers.mysql.schema.update_columns_with_constraints') as mock_update_columns,
        patch(
            'supabase_pydantic.db.marshalers.mysql.schema.update_column_constraint_definitions'
        ) as mock_update_definitions,
        patch('supabase_pydantic.db.marshalers.mysql.schema.analyze_bridge_tables') as mock_analyze_bridge,
        patch('supabase_pydantic.db.marshalers.mysql.schema.analyze_table_relationships') as mock_analyze_relationships,
        patch('supabase_pydantic.db.marshalers.mysql.schema.logger') as mock_logger,
    ):
        # Configure mocks
        mock_get_details.return_value = sample_tables
        mock_get_enum_types.return_value = ['mocked_enum']

        # Call the method
        result = schema_marshaler.construct_table_info(
            table_data, column_data, fk_data, constraint_data, type_data, type_mapping_data, schema
        )

        # Verify all functions were called with correct parameters
        mock_get_details.assert_called_once()
        mock_add_fk.assert_called_once_with(sample_tables, fk_data)
        mock_add_constraints.assert_called_once()
        mock_add_relationships.assert_called_once_with(sample_tables, fk_data)
        mock_get_enum_types.assert_called_once_with(type_data, schema)
        mock_add_types.assert_called_once_with(sample_tables, schema, ['mocked_enum'], type_mapping_data)
        mock_update_columns.assert_called_once_with(sample_tables)
        mock_update_definitions.assert_called_once_with(sample_tables)
        mock_analyze_bridge.assert_called_once_with(sample_tables)

        # analyze_table_relationships should be called twice
        assert mock_analyze_relationships.call_count == 2
        mock_analyze_relationships.assert_has_calls([call(sample_tables), call(sample_tables)])

        # Verify logging calls
        assert mock_logger.debug.call_count >= 5

        # Verify result is a list of table values
        assert result == list(sample_tables.values())


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_enum_types_dict_format(sample_enum_data):
    """Test get_enum_types function with dict format data."""
    result = get_enum_types(sample_enum_data, 'test_schema')

    # Should return 2 enums that match the schema
    assert len(result) == 2

    # Verify the first enum
    assert result[0].type_name == 'status_enum'
    assert result[0].namespace == 'test_schema'
    assert result[0].owner == 'admin'
    assert result[0].category == 'E'
    assert result[0].is_defined is True
    assert result[0].type == 'e'
    assert result[0].enum_values == ['pending', 'active', 'inactive']

    # Verify the second enum
    assert result[1].type_name == 'post_status'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_enum_types_tuple_format():
    """Test get_enum_types function with tuple format data."""
    tuple_data = [
        ('status_enum', 'test_schema', 'admin', 'E', True, 'e', ['pending', 'active', 'inactive']),
        ('post_status', 'test_schema', 'admin', 'E', True, 'e', ['draft', 'published', 'archived']),
        # A non-enum type
        ('some_other_type', 'test_schema', 'admin', 'D', True, 'd', None),
        # Enum in a different schema
        ('other_schema_enum', 'other_schema', 'admin', 'E', True, 'e', ['one', 'two', 'three']),
    ]

    result = get_enum_types(tuple_data, 'test_schema')

    # Should return 2 enums that match the schema
    assert len(result) == 2

    # Verify the first enum
    assert result[0].type_name == 'status_enum'
    assert result[0].namespace == 'test_schema'
    assert result[0].enum_values == ['pending', 'active', 'inactive']


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_get_enum_types_error_handling():
    """Test get_enum_types function error handling with malformed data."""
    # Malformed tuple with incorrect number of elements
    malformed_data = [
        ('status_enum', 'test_schema', 'admin'),  # Missing elements
    ]

    with patch('supabase_pydantic.db.marshalers.mysql.schema.logger') as mock_logger:
        result = get_enum_types(malformed_data, 'test_schema')

        # Should return empty list as no valid enums could be processed
        assert result == []

        # Should log an error
        mock_logger.error.assert_called_once()
        assert 'Error unpacking enum type' in mock_logger.error.call_args[0][0]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_mysql_user_defined_types_to_tables_dict_format(sample_tables, sample_enum_mapping_data):
    """Test add_mysql_user_defined_types_to_tables function with dict format data."""
    # Create sample UserEnumType objects
    enums = [
        UserEnumType(
            type_name='status_enum',
            namespace='test_schema',
            owner='admin',
            category='E',
            is_defined=True,
            type='e',
            enum_values=['pending', 'active', 'inactive'],
        ),
        UserEnumType(
            type_name='post_status',
            namespace='test_schema',
            owner='admin',
            category='E',
            is_defined=True,
            type='e',
            enum_values=['draft', 'published', 'archived'],
        ),
    ]

    # Call the function
    add_mysql_user_defined_types_to_tables(sample_tables, 'test_schema', enums, sample_enum_mapping_data)

    # Verify that enum_info was added to the columns
    users_table = sample_tables[('test_schema', 'users')]
    status_column = next(col for col in users_table.columns if col.name == 'status')
    assert status_column.enum_info is not None
    assert status_column.enum_info.name == 'status_enum'
    assert status_column.enum_info.values == ['pending', 'active', 'inactive']
    assert status_column.enum_info.schema == 'test_schema'

    # Verify that user_defined_values was set for backward compatibility
    assert status_column.user_defined_values == ['pending', 'active', 'inactive']

    # Check posts table too
    posts_table = sample_tables[('test_schema', 'posts')]
    status_column = next(col for col in posts_table.columns if col.name == 'status')
    assert status_column.enum_info is not None
    assert status_column.enum_info.name == 'post_status'
    assert status_column.enum_info.values == ['draft', 'published', 'archived']


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_mysql_user_defined_types_to_tables_tuple_format(sample_tables):
    """Test add_mysql_user_defined_types_to_tables function with tuple format data."""
    # Create sample UserEnumType objects
    enums = [
        UserEnumType(
            type_name='status_enum',
            namespace='test_schema',
            owner='admin',
            category='E',
            is_defined=True,
            type='e',
            enum_values=['pending', 'active', 'inactive'],
        ),
    ]

    # Create tuple format mapping data
    tuple_mapping_data = [
        ('status', 'users', 'test_schema', 'status_enum', 'E', 'User status enum'),
    ]

    # Call the function
    add_mysql_user_defined_types_to_tables(sample_tables, 'test_schema', enums, tuple_mapping_data)

    # Verify that enum_info was added to the column
    users_table = sample_tables[('test_schema', 'users')]
    status_column = next(col for col in users_table.columns if col.name == 'status')
    assert status_column.enum_info is not None
    assert status_column.enum_info.name == 'status_enum'
    assert status_column.enum_info.values == ['pending', 'active', 'inactive']


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_mysql_user_defined_types_to_tables_error_handling(sample_tables):
    """Test add_mysql_user_defined_types_to_tables function error handling with malformed data."""
    # Create sample UserEnumType objects
    enums = [
        UserEnumType(
            type_name='status_enum',
            namespace='test_schema',
            owner='admin',
            category='E',
            is_defined=True,
            type='e',
            enum_values=['pending', 'active', 'inactive'],
        ),
    ]

    # Malformed tuple with incorrect number of elements
    malformed_data = [
        ('status', 'users'),  # Missing elements
    ]

    with patch('supabase_pydantic.db.marshalers.mysql.schema.logger') as mock_logger:
        # Call the function
        add_mysql_user_defined_types_to_tables(sample_tables, 'test_schema', enums, malformed_data)

        # Should log an error
        mock_logger.error.assert_called_once()
        assert 'Error unpacking enum type mapping' in mock_logger.error.call_args[0][0]

        # No enum info should be added since the mapping couldn't be processed
        users_table = sample_tables[('test_schema', 'users')]
        status_column = next(col for col in users_table.columns if col.name == 'status')
        assert status_column.enum_info is None


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_mysql_user_defined_types_to_tables_array_columns(sample_tables):
    """Test handling of array columns with enum element types."""
    # Create sample UserEnumType objects
    enums = [
        UserEnumType(
            type_name='tag_type',
            namespace='test_schema',
            owner='admin',
            category='E',
            is_defined=True,
            type='e',
            enum_values=['news', 'tech', 'sports'],
        ),
    ]

    # Update the tags column to have an array element type that matches the enum
    posts_table = sample_tables[('test_schema', 'posts')]
    tags_column = next(col for col in posts_table.columns if col.name == 'tags')
    tags_column.array_element_type = 'tag_type'

    # No mappings needed since we're testing array element type detection
    mappings = []

    # Call the function
    add_mysql_user_defined_types_to_tables(sample_tables, 'test_schema', enums, mappings)

    # Verify that enum_info was added to the array column
    assert tags_column.enum_info is not None
    assert tags_column.enum_info.name == 'tag_type'
    assert tags_column.enum_info.values == ['news', 'tech', 'sports']
    assert tags_column.enum_info.schema == 'test_schema'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_mysql_user_defined_types_to_tables_qualified_array_type(sample_tables):
    """Test handling of array columns with qualified enum element types (schema.typename)."""
    # Create sample UserEnumType objects
    enums = [
        UserEnumType(
            type_name='tag_type',
            namespace='test_schema',
            owner='admin',
            category='E',
            is_defined=True,
            type='e',
            enum_values=['news', 'tech', 'sports'],
        ),
    ]

    # Update the tags column to have a qualified array element type
    posts_table = sample_tables[('test_schema', 'posts')]
    tags_column = next(col for col in posts_table.columns if col.name == 'tags')
    tags_column.array_element_type = 'test_schema.tag_type'  # Qualified with schema

    # No mappings needed since we're testing array element type detection
    mappings = []

    # Call the function
    add_mysql_user_defined_types_to_tables(sample_tables, 'test_schema', enums, mappings)

    # Verify that enum_info was added to the array column
    assert tags_column.enum_info is not None
    assert tags_column.enum_info.name == 'tag_type'
    assert tags_column.enum_info.values == ['news', 'tech', 'sports']
