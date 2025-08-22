"""Tests for relationship marshaler functions in supabase_pydantic.db.marshalers.relationships."""

from unittest.mock import MagicMock

import pytest

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.models import (
    ColumnInfo,
    ForeignKeyInfo,
    RelationshipInfo,
    TableInfo,
)
from supabase_pydantic.db.marshalers.relationships import (
    add_relationships_to_table_details,
    analyze_bridge_tables,
    is_bridge_table,
)


@pytest.fixture
def bridge_table_setup():
    columns = [
        ColumnInfo(name='user_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='role_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(
            name='created_at', primary=False, is_foreign_key=False, post_gres_datatype='timestamp', datatype='str'
        ),
    ]
    foreign_keys = [
        ForeignKeyInfo(
            column_name='user_id', foreign_table_name='users', foreign_column_name='id', constraint_name='fk_user_id'
        ),
        ForeignKeyInfo(
            column_name='role_id', foreign_table_name='roles', foreign_column_name='id', constraint_name='fk_role_id'
        ),
    ]
    return TableInfo(name='user_roles', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def non_bridge_table_setup():
    columns = [
        ColumnInfo(name='id', primary=True, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='info', primary=False, is_foreign_key=False, post_gres_datatype='text', datatype='str'),
    ]
    foreign_keys = []
    return TableInfo(name='simple_table', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def no_primary_bridge_table_setup():
    columns = [
        ColumnInfo(name='user_id', primary=False, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='role_id', primary=False, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(
            name='created_at', primary=False, is_foreign_key=False, post_gres_datatype='timestamp', datatype='str'
        ),
    ]
    foreign_keys = [
        ForeignKeyInfo(
            column_name='user_id', foreign_table_name='users', foreign_column_name='id', constraint_name='fk_user_id'
        ),
        ForeignKeyInfo(
            column_name='role_id', foreign_table_name='roles', foreign_column_name='id', constraint_name='fk_role_id'
        ),
    ]
    return TableInfo(name='user_roles', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def primary_foreign_and_col_primary_unequal_table_setup():
    columns = [
        ColumnInfo(name='user_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(name='role_id', primary=True, is_foreign_key=True, post_gres_datatype='uuid', datatype='str'),
        ColumnInfo(
            name='created_at', primary=True, is_foreign_key=False, post_gres_datatype='timestamp', datatype='str'
        ),
    ]
    foreign_keys = [
        ForeignKeyInfo(
            column_name='user_id', foreign_table_name='users', foreign_column_name='id', constraint_name='fk_user_id'
        ),
        ForeignKeyInfo(
            column_name='role_id', foreign_table_name='roles', foreign_column_name='id', constraint_name='fk_role_id'
        ),
    ]
    return TableInfo(name='user_roles', schema='public', columns=columns, foreign_keys=foreign_keys, is_bridge=False)


@pytest.fixture
def setup_analyze_tables():
    # Create two tables with a simple one-to-many relationship
    user_table = TableInfo(
        name='users',
        schema='public',
        columns=[
            ColumnInfo(
                name='id', primary=True, is_unique=True, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'
            ),
            ColumnInfo(
                name='username',
                primary=False,
                is_unique=True,
                is_foreign_key=False,
                post_gres_datatype='text',
                datatype='str',
            ),
        ],
        foreign_keys=[],
    )

    order_table = TableInfo(
        name='orders',
        schema='public',
        columns=[
            ColumnInfo(
                name='id', primary=True, is_unique=True, is_foreign_key=False, post_gres_datatype='uuid', datatype='str'
            ),
            ColumnInfo(
                name='user_id',
                primary=False,
                is_unique=False,
                is_foreign_key=True,
                post_gres_datatype='uuid',
                datatype='str',
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='fk_user_id',
                column_name='user_id',
                foreign_table_name='users',
                foreign_column_name='id',
                relation_type=None,
            )
        ],
    )
    return {'public.users': user_table, 'public.orders': order_table}


@pytest.fixture
def relationship_tables():
    # Create tables with various relationship types
    user_table = TableInfo(
        name='users',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(
                name='profile_id', is_foreign_key=True, is_unique=True, post_gres_datatype='uuid', datatype='str'
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='profile_id',
                foreign_table_name='profiles',
                foreign_column_name='id',
                constraint_name='fk_user_profile',
            ),
        ],
    )

    profile_table = TableInfo(
        name='profiles',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
        ],
    )

    post_table = TableInfo(
        name='posts',
        schema='public',
        columns=[
            ColumnInfo(name='id', primary=True, is_unique=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(name='user_id', is_foreign_key=True, is_unique=False, post_gres_datatype='uuid', datatype='str'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='user_id',
                foreign_table_name='users',
                foreign_column_name='id',
                constraint_name='fk_post_user',
            ),
        ],
    )

    return {
        ('public', 'users'): user_table,
        ('public', 'profiles'): profile_table,
        ('public', 'posts'): post_table,
    }


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_is_bridge_table(
    bridge_table_setup,
    non_bridge_table_setup,
    no_primary_bridge_table_setup,
    primary_foreign_and_col_primary_unequal_table_setup,
):
    assert is_bridge_table(bridge_table_setup) is True, 'Should identify as a bridge table'
    assert not is_bridge_table(non_bridge_table_setup), 'Should not identify as a bridge table'
    assert not is_bridge_table(no_primary_bridge_table_setup), 'Should not identify as a bridge table'
    assert not is_bridge_table(primary_foreign_and_col_primary_unequal_table_setup), (
        'Should not identify as a bridge table'
    )


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_analyze_bridge_tables(
    bridge_table_setup,
    non_bridge_table_setup,
):
    tables = {
        'user_roles': bridge_table_setup,
        'simple_table': non_bridge_table_setup,
    }
    analyze_bridge_tables(tables)
    assert tables['user_roles'].is_bridge is True, 'user_roles should be marked as a bridge table'
    assert not tables['simple_table'].is_bridge, 'simple_table should not be marked as a bridge table'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_analyze_table_relationships(setup_analyze_tables):
    from supabase_pydantic.db.marshalers import analyze_table_relationships

    analyze_table_relationships(setup_analyze_tables)

    # Check basic many-to-one relationship
    assert setup_analyze_tables['public.orders'].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE

    # Check for automatically added reciprocal foreign key in users table
    assert len(setup_analyze_tables['public.users'].foreign_keys) == 1
    assert setup_analyze_tables['public.users'].foreign_keys[0].relation_type == RelationType.ONE_TO_MANY
    assert setup_analyze_tables['public.users'].foreign_keys[0].foreign_table_name == 'orders'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_no_foreign_table(setup_analyze_tables):
    from supabase_pydantic.db.marshalers import analyze_table_relationships

    # Add a foreign key with a non-existent table
    setup_analyze_tables['public.orders'].foreign_keys.append(
        ForeignKeyInfo(
            constraint_name='fk_nonexistent',
            column_name='user_id',
            foreign_table_name='nonexistent',
            foreign_column_name='id',
            relation_type=None,
        )
    )
    analyze_table_relationships(setup_analyze_tables)
    # Verify that no changes occurred for the non-existent table foreign key
    assert 'public.nonexistent' not in setup_analyze_tables


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_reciprocal_foreign_keys(setup_analyze_tables):
    from supabase_pydantic.db.marshalers import analyze_table_relationships

    # Add a new column to users for order_id
    setup_analyze_tables['public.users'].columns.append(
        ColumnInfo(
            name='order_id',
            primary=False,
            is_unique=False,
            is_foreign_key=True,
            post_gres_datatype='uuid',
            datatype='str',
        )
    )
    # Add reciprocal foreign key in users table
    setup_analyze_tables['public.users'].foreign_keys.append(
        ForeignKeyInfo(
            constraint_name='fk_order_id',
            column_name='order_id',
            foreign_table_name='orders',
            foreign_column_name='id',
            relation_type=None,
        )
    )
    analyze_table_relationships(setup_analyze_tables)
    # Expecting a many-to-one relationship in both directions
    assert setup_analyze_tables['public.orders'].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE
    assert setup_analyze_tables['public.users'].foreign_keys[0].relation_type == RelationType.MANY_TO_ONE


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_add_relationships_to_table_details():
    # Mocking the table structures
    table1 = MagicMock()
    table1.foreign_keys = [MagicMock(foreign_table_name='related_table', foreign_column_name='id')]
    table1.columns = [MagicMock(name='id'), MagicMock(name='column1')]

    related_table = MagicMock()
    related_table.columns = [MagicMock(name='id'), MagicMock(name='column2')]

    tables = {('schema1', 'table1'): table1, ('schema1', 'related_table'): related_table}

    fk_details = [('schema1', 'table1', 'column1', 'schema1', 'related_table', 'id', 'fk1')]

    # Mock the relationships list where relationships will be added
    table1.relationships = []

    # Call the function
    add_relationships_to_table_details(tables, fk_details)

    # Assert that the relationship was correctly added
    expected_relationship = RelationshipInfo(
        table_name='table1',
        related_table_name='related_table',
        relation_type=RelationType.ONE_TO_MANY,
    )

    assert len(table1.relationships) == 1
    assert table1.relationships[0].table_name == expected_relationship.table_name
    assert table1.relationships[0].related_table_name == expected_relationship.related_table_name
    assert table1.relationships[0].relation_type == expected_relationship.relation_type


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_relationship_types(relationship_tables):
    from supabase_pydantic.db.marshalers import analyze_table_relationships

    # Test ONE_TO_ONE relationship (user -> profile)
    analyze_table_relationships(relationship_tables)
    user_table = relationship_tables[('public', 'users')]

    # Check user -> profile relationship (ONE_TO_ONE)
    user_profile_rel = next(rel for rel in user_table.foreign_keys if rel.foreign_table_name == 'profiles')
    assert user_profile_rel.relation_type == RelationType.ONE_TO_ONE

    # Check post -> user relationship (MANY_TO_ONE)
    post_table = relationship_tables[('public', 'posts')]
    post_user_rel = next(rel for rel in post_table.foreign_keys if rel.foreign_table_name == 'users')
    assert post_user_rel.relation_type == RelationType.MANY_TO_ONE
