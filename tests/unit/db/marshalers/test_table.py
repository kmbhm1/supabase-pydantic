"""Tests for table marshaler functions in supabase_pydantic.db.marshalers.table."""

import pytest

from supabase_pydantic.db.models import (
    ColumnInfo,
    TableInfo,
    ConstraintInfo,
)


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_TableInfo_methods():
    # Create a simple table info object
    table = TableInfo(
        name='users',
        schema='public',
        table_type='BASE TABLE',
        columns=[
            ColumnInfo(name='id', primary=True, post_gres_datatype='uuid', datatype='str'),
            ColumnInfo(name='email', post_gres_datatype='text', datatype='str'),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='pk_users',
                columns=['id'],
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (id)',
            )
        ],
    )

    # Test string representation
    assert 'TableInfo' in str(table)
    assert 'users' in str(table)

    # Test as_dict method
    table_dict = table.as_dict()
    assert table_dict['name'] == 'users'
    assert table_dict['schema'] == 'public'
    assert len(table_dict['columns']) == 2
    assert len(table_dict['constraints']) == 1

    # Find column by name
    primary_columns = table.get_primary_columns()
    assert len(primary_columns) == 1
    assert primary_columns[0].name == 'id'
    assert primary_columns[0].primary is True

    # Test finding a column that doesn't exist
    non_primary_columns = [col for col in table.columns if col.name == 'nonexistent']
    assert len(non_primary_columns) == 0

    # Test get_primary_columns method
    primary_keys = table.get_primary_columns()
    assert len(primary_keys) == 1
    assert primary_keys[0].name == 'id'

    # Test primary_key method to check if there is a primary key
    assert len(table.primary_key()) > 0

    # Create a table without primary keys
    table_no_pk = TableInfo(
        name='logs',
        schema='public',
        table_type='BASE TABLE',
        columns=[
            ColumnInfo(name='message', post_gres_datatype='text', datatype='str'),
            ColumnInfo(name='timestamp', post_gres_datatype='timestamp', datatype='datetime'),
        ],
    )
    # Test a table without primary keys
    assert len(table_no_pk.primary_key()) == 0
    assert len(table_no_pk.get_primary_columns()) == 0


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_ConstraintInfo_methods():
    # Create a constraint info object
    constraint = ConstraintInfo(
        constraint_name='pk_users',
        columns=['id'],
        raw_constraint_type='p',
        constraint_definition='PRIMARY KEY (id)',
    )

    # Test string representation
    assert 'ConstraintInfo' in str(constraint)
    assert 'pk_users' in str(constraint)

    # Test as_dict method
    constraint_dict = constraint.as_dict()
    assert constraint_dict['constraint_name'] == 'pk_users'
    assert constraint_dict['columns'] == ['id']
    assert constraint_dict['raw_constraint_type'] == 'p'

    # Test constraint_type method
    assert constraint.constraint_type() == 'PRIMARY KEY'

    # Test other constraint types
    unique_constraint = ConstraintInfo(
        constraint_name='unique_email',
        columns=['email'],
        raw_constraint_type='u',
        constraint_definition='UNIQUE (email)',
    )
    assert unique_constraint.constraint_type() == 'UNIQUE'

    fk_constraint = ConstraintInfo(
        constraint_name='fk_user_role',
        columns=['role_id'],
        raw_constraint_type='f',
        constraint_definition='FOREIGN KEY (role_id) REFERENCES roles(id)',
    )
    assert fk_constraint.constraint_type() == 'FOREIGN KEY'

    check_constraint = ConstraintInfo(
        constraint_name='check_age',
        columns=['age'],
        raw_constraint_type='c',
        constraint_definition='CHECK (age >= 0)',
    )
    assert check_constraint.constraint_type() == 'CHECK'

    # Test constraint with invalid type
    invalid_constraint = ConstraintInfo(
        constraint_name='invalid',
        columns=['col'],
        raw_constraint_type='x',  # Invalid type
        constraint_definition='INVALID',
    )
    assert invalid_constraint.constraint_type() == 'EXCLUDE'


@pytest.mark.unit
@pytest.mark.db
@pytest.mark.marshalers
def test_ColumnInfo_methods():
    # Create a column info object
    column = ColumnInfo(
        name='id',
        primary=True,
        is_unique=True,
        is_foreign_key=False,
        post_gres_datatype='uuid',
        datatype='str',
        default='uuid_generate_v4()',
    )

    # Test string representation
    assert 'ColumnInfo' in str(column)
    assert 'id' in str(column)

    # Test as_dict method
    column_dict = column.as_dict()
    assert column_dict['name'] == 'id'
    assert column_dict['primary'] is True
    assert column_dict['is_unique'] is True
    assert column_dict['post_gres_datatype'] == 'uuid'
    assert column_dict['datatype'] == 'str'

    # Create column with user defined values
    enum_column = ColumnInfo(
        name='status',
        post_gres_datatype='user-defined',
        datatype='str',
        user_defined_values=['active', 'inactive', 'suspended'],
    )
    enum_dict = enum_column.as_dict()
    assert enum_dict['user_defined_values'] == ['active', 'inactive', 'suspended']
