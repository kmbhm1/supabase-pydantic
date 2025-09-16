"""Additional tests for schema marshaler functions in supabase_pydantic.db.marshalers.schema."""

import pytest
from unittest.mock import patch

from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.models import (
    ColumnInfo,
    TableInfo,
)
from supabase_pydantic.db.marshalers.schema import (
    add_user_defined_types_to_tables,
    construct_table_info,
)
from supabase_pydantic.db.database_type import DatabaseType


@pytest.fixture
def array_column_tables():
    """Fixture for tables with array columns that may contain enum types."""
    return {
        ('public', 'test_table'): TableInfo(
            name='test_table',
            schema='public',
            columns=[
                # Regular column
                ColumnInfo(
                    name='id',
                    user_defined_values=None,
                    post_gres_datatype='uuid',
                    datatype='str',
                ),
                # Array column with enum element type
                ColumnInfo(
                    name='tags',
                    user_defined_values=None,
                    post_gres_datatype='ARRAY',
                    datatype='list[str]',
                    array_element_type='tag_type',
                ),
                # Array column with array brackets in element type
                ColumnInfo(
                    name='categories',
                    user_defined_values=None,
                    post_gres_datatype='ARRAY',
                    datatype='list[str]',
                    array_element_type='category_type[]',
                ),
                # Array column with qualified type name
                ColumnInfo(
                    name='status_codes',
                    user_defined_values=None,
                    post_gres_datatype='ARRAY',
                    datatype='list[str]',
                    array_element_type='public.status_type',
                ),
                # Array column with enum_info already set (should be skipped)
                ColumnInfo(
                    name='priorities',
                    user_defined_values=None,
                    post_gres_datatype='ARRAY',
                    datatype='list[str]',
                    array_element_type='priority_type',
                    enum_info=EnumInfo(name='priority_type', values=['high', 'medium', 'low'], schema='public'),
                ),
                # Non-array column (should be skipped)
                ColumnInfo(
                    name='name',
                    user_defined_values=None,
                    post_gres_datatype='varchar',
                    datatype='str',
                ),
            ],
        )
    }


@pytest.fixture
def array_enum_types():
    """Fixture for enum types that might be used in array columns."""
    return [
        # Matches 'tags' column's array_element_type
        ('tag_type', 'public', 'owner', 'E', True, 'e', ['red', 'green', 'blue']),
        # Matches 'categories' column's array_element_type after removing brackets
        ('category_type', 'public', 'owner', 'E', True, 'e', ['A', 'B', 'C']),
        # Matches 'status_codes' column's array_element_type (qualified name)
        ('status_type', 'public', 'owner', 'E', True, 'e', ['active', 'inactive', 'pending']),
        # No matching column
        ('other_type', 'public', 'owner', 'E', True, 'e', ['x', 'y', 'z']),
    ]


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_user_defined_types_array_columns(array_column_tables, array_enum_types):
    """Test adding enum types to array columns."""
    enum_type_mapping = []  # Not needed for this test as we're testing array handling

    # Call the function
    add_user_defined_types_to_tables(
        array_column_tables, 'public', array_enum_types, enum_type_mapping, DatabaseType.POSTGRES
    )

    # Get the test table
    table = array_column_tables[('public', 'test_table')]

    # Check tags column got enum_info assigned
    tags_column = next(col for col in table.columns if col.name == 'tags')
    assert tags_column.enum_info is not None
    assert tags_column.enum_info.name == 'tag_type'
    assert tags_column.enum_info.values == ['red', 'green', 'blue']

    # Check categories column (with brackets in element type)
    categories_column = next(col for col in table.columns if col.name == 'categories')
    assert categories_column.enum_info is not None
    assert categories_column.enum_info.name == 'category_type'
    assert categories_column.enum_info.values == ['A', 'B', 'C']

    # Check status_codes column (with qualified name)
    status_codes_column = next(col for col in table.columns if col.name == 'status_codes')
    assert status_codes_column.enum_info is not None
    assert status_codes_column.enum_info.name == 'status_type'
    assert status_codes_column.enum_info.values == ['active', 'inactive', 'pending']

    # Check that priorities column enum_info was not changed
    priorities_column = next(col for col in table.columns if col.name == 'priorities')
    assert priorities_column.enum_info.values == ['high', 'medium', 'low']

    # Check that non-array column was not affected
    name_column = next(col for col in table.columns if col.name == 'name')
    assert name_column.enum_info is None


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_construct_table_info():
    """Test the construct_table_info function which integrates multiple processing steps."""
    # Mock column details
    column_details = [
        ('public', 'users', 'id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE', None, 'uuid', None, None),
        ('public', 'users', 'email', None, 'YES', 'text', 255, 'BASE TABLE', None, 'text', None, None),
        ('public', 'posts', 'id', 'uuid_generate_v4()', 'NO', 'uuid', None, 'BASE TABLE', None, 'uuid', None, None),
        ('public', 'posts', 'user_id', None, 'YES', 'uuid', None, 'BASE TABLE', None, 'uuid', None, None),
    ]

    # Mock foreign key details
    fk_details = [('posts', 'user_id', 'users', 'id', 'CASCADE', 'NO ACTION', 'fk_posts_user_id')]

    # Mock constraints
    constraints = [
        ('pk_users', 'users', ['id'], 'PRIMARY KEY', 'PRIMARY KEY (id)'),
        ('pk_posts', 'posts', ['id'], 'PRIMARY KEY', 'PRIMARY KEY (id)'),
    ]

    # Mock enum types and mappings
    enum_types = [
        ('status', 'public', 'owner', 'E', True, 'e', ['draft', 'published', 'archived']),
    ]
    enum_type_mapping = [
        ('status', 'posts', 'public', 'status', 'E', 'Post status'),
    ]

    # Use patch to avoid having to mock every function called by construct_table_info
    with patch('supabase_pydantic.db.marshalers.schema.add_foreign_key_info_to_table_details'):
        with patch('supabase_pydantic.db.marshalers.schema.add_constraints_to_table_details'):
            with patch('supabase_pydantic.db.marshalers.schema.add_relationships_to_table_details'):
                with patch('supabase_pydantic.db.marshalers.schema.add_user_defined_types_to_tables'):
                    with patch('supabase_pydantic.db.marshalers.schema.update_columns_with_constraints'):
                        with patch('supabase_pydantic.db.marshalers.schema.update_column_constraint_definitions'):
                            with patch('supabase_pydantic.db.marshalers.schema.analyze_bridge_tables'):
                                with patch('supabase_pydantic.db.marshalers.schema.analyze_table_relationships'):
                                    # Call the function
                                    result = construct_table_info(
                                        column_details=column_details,
                                        fk_details=fk_details,
                                        constraints=constraints,
                                        enum_types=enum_types,
                                        enum_type_mapping=enum_type_mapping,
                                        schema='public',
                                    )

                                    # Verify result format and basic content
                                    assert isinstance(result, list)
                                    assert len(result) == 2

                                    # Verify table info objects
                                    table_names = {table.name for table in result}
                                    assert 'users' in table_names
                                    assert 'posts' in table_names

                                    # Find tables by name
                                    users_table = next(table for table in result if table.name == 'users')
                                    posts_table = next(table for table in result if table.name == 'posts')

                                    # Check column counts
                                    assert len(users_table.columns) == 2
                                    assert len(posts_table.columns) == 2
