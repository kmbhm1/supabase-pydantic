"""Tests for MySQL relationship marshaler implementation."""

import pytest
from unittest.mock import patch

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.mysql.relationship import MySQLRelationshipMarshaler
from supabase_pydantic.db.models import TableInfo, ColumnInfo, ConstraintInfo, RelationshipInfo


@pytest.fixture
def marshaler():
    """Fixture to create a MySQLRelationshipMarshaler instance."""
    return MySQLRelationshipMarshaler()


@pytest.fixture
def sample_tables():
    """Create sample tables for testing relationships."""
    # Create users table with ID as primary key
    users_columns = [
        ColumnInfo(
            name='id', post_gres_datatype='int', datatype='int', is_nullable=False, is_unique=True, primary=True
        ),
        ColumnInfo(name='email', post_gres_datatype='varchar', datatype='varchar', is_nullable=False, is_unique=True),
        ColumnInfo(name='name', post_gres_datatype='varchar', datatype='varchar', is_nullable=False),
    ]
    users_constraints = [
        ConstraintInfo(
            constraint_name='pk_users',
            raw_constraint_type='p',
            columns=['id'],
            constraint_definition='PRIMARY KEY (id)',
        )
    ]
    users_table = TableInfo(
        name='users',
        schema='test_schema',
        table_type='BASE TABLE',
        columns=users_columns,
        constraints=users_constraints,
    )

    # Create posts table with user_id as foreign key
    posts_columns = [
        ColumnInfo(
            name='id', post_gres_datatype='int', datatype='int', is_nullable=False, is_unique=True, primary=True
        ),
        ColumnInfo(name='user_id', post_gres_datatype='int', datatype='int', is_nullable=False),
        ColumnInfo(name='title', post_gres_datatype='varchar', datatype='varchar', is_nullable=False),
    ]
    posts_constraints = [
        ConstraintInfo(
            constraint_name='pk_posts',
            raw_constraint_type='p',
            columns=['id'],
            constraint_definition='PRIMARY KEY (id)',
        )
    ]
    posts_table = TableInfo(
        name='posts',
        schema='test_schema',
        table_type='BASE TABLE',
        columns=posts_columns,
        constraints=posts_constraints,
    )

    # Create tags table
    tags_columns = [
        ColumnInfo(
            name='id', post_gres_datatype='int', datatype='int', is_nullable=False, is_unique=True, primary=True
        ),
        ColumnInfo(name='name', post_gres_datatype='varchar', datatype='varchar', is_nullable=False, is_unique=True),
    ]
    tags_constraints = [
        ConstraintInfo(
            constraint_name='pk_tags', raw_constraint_type='p', columns=['id'], constraint_definition='PRIMARY KEY (id)'
        )
    ]
    tags_table = TableInfo(
        name='tags', schema='test_schema', table_type='BASE TABLE', columns=tags_columns, constraints=tags_constraints
    )

    # Create post_tags bridge table
    post_tags_columns = [
        ColumnInfo(name='post_id', post_gres_datatype='int', datatype='int', is_nullable=False, primary=True),
        ColumnInfo(name='tag_id', post_gres_datatype='int', datatype='int', is_nullable=False, primary=True),
    ]
    post_tags_constraints = [
        ConstraintInfo(
            constraint_name='pk_post_tags',
            raw_constraint_type='p',
            columns=['post_id', 'tag_id'],
            constraint_definition='PRIMARY KEY (post_id, tag_id)',
        )
    ]
    post_tags_table = TableInfo(
        name='post_tags',
        schema='test_schema',
        table_type='BASE TABLE',
        columns=post_tags_columns,
        constraints=post_tags_constraints,
    )

    # Create profile table for one-to-one relationship with users
    profile_columns = [
        ColumnInfo(
            name='user_id', post_gres_datatype='int', datatype='int', is_nullable=False, is_unique=True, primary=True
        ),
        ColumnInfo(name='bio', post_gres_datatype='text', datatype='text', is_nullable=True),
    ]
    profile_constraints = [
        ConstraintInfo(
            constraint_name='pk_profile',
            raw_constraint_type='p',
            columns=['user_id'],
            constraint_definition='PRIMARY KEY (user_id)',
        )
    ]
    profile_table = TableInfo(
        name='profile',
        schema='test_schema',
        table_type='BASE TABLE',
        columns=profile_columns,
        constraints=profile_constraints,
    )

    # Dictionary with all tables
    tables = {
        ('test_schema', 'users'): users_table,
        ('test_schema', 'posts'): posts_table,
        ('test_schema', 'tags'): tags_table,
        ('test_schema', 'post_tags'): post_tags_table,
        ('test_schema', 'profile'): profile_table,
    }
    return tables


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_type_one_to_many(marshaler, sample_tables):
    """Test determining one-to-many relationship type."""
    source_table = sample_tables[('test_schema', 'users')]
    target_table = sample_tables[('test_schema', 'posts')]
    source_column = 'id'
    target_column = 'user_id'

    result = marshaler.determine_relationship_type(source_table, target_table, source_column, target_column)

    # The user's ID (unique) to posts.user_id (non-unique) should be ONE_TO_MANY
    assert result == RelationType.ONE_TO_MANY


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_type_one_to_one(marshaler, sample_tables):
    """Test determining one-to-one relationship type."""
    source_table = sample_tables[('test_schema', 'users')]
    target_table = sample_tables[('test_schema', 'profile')]
    source_column = 'id'
    target_column = 'user_id'

    result = marshaler.determine_relationship_type(source_table, target_table, source_column, target_column)

    # The user's ID (unique) to profile.user_id (unique) should be ONE_TO_ONE
    assert result == RelationType.ONE_TO_ONE


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_type_many_to_many(marshaler, sample_tables):
    """Test determining many-to-many relationship type."""
    source_table = sample_tables[('test_schema', 'posts')]
    target_table = sample_tables[('test_schema', 'tags')]
    source_column = 'id'
    target_column = 'id'

    # We'll patch determine_rel_type to simulate many-to-many detection
    with patch('supabase_pydantic.db.marshalers.mysql.relationship.determine_rel_type') as mock_determine_rel_type:
        mock_determine_rel_type.return_value = (RelationType.MANY_TO_MANY, RelationType.MANY_TO_MANY)

        result = marshaler.determine_relationship_type(source_table, target_table, source_column, target_column)

        # Should match whatever the patched function returns
        assert result == RelationType.MANY_TO_MANY
        mock_determine_rel_type.assert_called_once()


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
@patch('supabase_pydantic.db.marshalers.mysql.relationship.analyze_relationships')
def test_analyze_table_relationships(mock_analyze, marshaler, sample_tables):
    """Test analyzing table relationships."""
    marshaler.analyze_table_relationships(sample_tables)

    # Verify analyze_relationships from shared module was called
    mock_analyze.assert_called_once_with(sample_tables)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_types_bidirectional(marshaler):
    """Test _determine_relationship_types with bidirectional relationships."""
    # Create mock table relationships
    table_relationships = {
        'users': [
            RelationshipInfo(
                table_name='users',
                related_table_name='posts',
                relation_type=None,  # To be determined by the function
            )
        ],
        'posts': [
            RelationshipInfo(
                table_name='posts',
                related_table_name='users',
                relation_type=None,  # To be determined by the function
            )
        ],
    }

    # Call the method
    marshaler._determine_relationship_types(table_relationships)

    # Check relationship types were correctly set
    # According to the implementation, when tables reference each other directly,
    # both relationships are set to MANY_TO_MANY
    assert table_relationships['users'][0].relation_type == RelationType.MANY_TO_MANY
    assert table_relationships['posts'][0].relation_type == RelationType.MANY_TO_MANY


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_types_many_to_many(marshaler):
    """Test _determine_relationship_types with many-to-many relationships."""
    # Create mock table relationships for many-to-many scenario
    table_relationships = {
        'posts': [RelationshipInfo(table_name='posts', related_table_name='tags', relation_type=None)],
        'tags': [RelationshipInfo(table_name='tags', related_table_name='posts', relation_type=None)],
    }

    # Call the method
    marshaler._determine_relationship_types(table_relationships)

    # Both should be set to MANY_TO_MANY because they reference each other
    assert table_relationships['posts'][0].relation_type == RelationType.MANY_TO_MANY
    assert table_relationships['tags'][0].relation_type == RelationType.MANY_TO_MANY


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_determine_relationship_types_unidirectional(marshaler):
    """Test _determine_relationship_types with unidirectional relationships."""
    # Create mock table relationships for unidirectional scenario
    table_relationships = {
        'posts': [RelationshipInfo(table_name='posts', related_table_name='categories', relation_type=None)],
        'categories': [],  # No relationship pointing back to posts
    }

    # Call the method
    marshaler._determine_relationship_types(table_relationships)

    # Should be set to MANY_TO_ONE for a unidirectional foreign key
    assert table_relationships['posts'][0].relation_type == RelationType.MANY_TO_ONE
