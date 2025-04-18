import json

from supabase_pydantic.util.constants import OrmType
from supabase_pydantic.util.dataclasses import ColumnInfo, ConstraintInfo, ForeignKeyInfo, TableInfo


def test_ConstraintInfo_methods():
    """Test ConstraintInfo methods."""
    from supabase_pydantic.util.dataclasses import ConstraintInfo

    constraint_info = ConstraintInfo(
        constraint_name='test',
        raw_constraint_type='p',
        constraint_definition='PRIMARY KEY (foo)',
        columns=['foo', 'bar'],
    )
    assert json.loads(str(constraint_info)) == {
        'constraint_name': 'test',
        'raw_constraint_type': 'p',
        'constraint_definition': 'PRIMARY KEY (foo)',
        'columns': ['foo', 'bar'],
    }
    assert constraint_info.constraint_type() == 'PRIMARY KEY'

    constraint_info.raw_constraint_type = 't'
    assert constraint_info.constraint_type() == 'OTHER'


def test_ColumnInfo_methods():
    """Test ColumnInfo methods."""
    column_info = ColumnInfo(
        name='id',
        post_gres_datatype='uuid',
        datatype='UUID',
        alias='foo',
        default='uuid_generate_v4()',
        max_length=None,
        is_nullable=False,
        primary=True,
        is_unique=True,
        is_foreign_key=True,
    )
    assert column_info.orm_imports(OrmType.PYDANTIC) == {'from pydantic import UUID4'}
    assert column_info.orm_imports(OrmType.SQLALCHEMY) == {'from sqlalchemy.dialects.postgresql import UUID'}
    assert column_info.orm_datatype(OrmType.PYDANTIC) == 'UUID4'
    assert column_info.orm_datatype(OrmType.SQLALCHEMY) == 'UUID'


def test_TableInfo_methods():
    """Test TableInfo methods."""
    table = TableInfo(
        name='test',
        schema='public',
        table_type='BASE TABLE',
        is_bridge=False,
        columns=[
            ColumnInfo(
                name='id',
                post_gres_datatype='uuid',
                datatype='UUID',
                alias='foo',
                default='uuid_generate_v4()',
                max_length=None,
                is_nullable=False,
                primary=True,
                is_unique=True,
                is_foreign_key=True,
            ),
            ColumnInfo(
                name='name',
                post_gres_datatype='text',
                datatype='str',
                alias='bar',
                default=None,
                max_length=255,
                is_nullable=False,
                primary=False,
                is_unique=False,
                is_foreign_key=False,
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='test',
                column_name='foo',
                foreign_table_name='bar',
                foreign_column_name='baz',
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='primary key',
                raw_constraint_type='p',
                constraint_definition='PRIMARY KEY (foo)',
                columns=['id'],
            ),
            ConstraintInfo(
                constraint_name='foreign key',
                raw_constraint_type='t',
                constraint_definition='FOREIGN KEY (bar) REFERENCES barz(baz)',
                columns=['bar'],
            ),
        ],
        generated_data=[],
    )

    assert len(table.columns) == 2
    table.add_column(
        ColumnInfo(
            name='test',
            post_gres_datatype='text',
            datatype='str',
            alias='bar',
            default=None,
            max_length=255,
            is_nullable=True,
            primary=False,
            is_unique=False,
            is_foreign_key=False,
        )
    )
    assert len(table.columns) == 3

    assert len(table.foreign_keys) == 1
    table.add_foreign_key(
        ForeignKeyInfo(
            constraint_name='test',
            column_name='foo',
            foreign_table_name='bar',
            foreign_column_name='baz',
        )
    )
    assert len(table.foreign_keys) == 2

    assert len(table.constraints) == 2
    table.add_constraint(
        ConstraintInfo(
            constraint_name='test',
            raw_constraint_type='t',
            constraint_definition='PRIMARY KEY (foo)',
            columns=['foo', 'bar'],
        )
    )
    assert len(table.constraints) == 3

    assert table.aliasing_in_columns() is True
    assert table.table_dependencies() == {'bar'}
    assert table.primary_key() == ['id']
    table.table_type = 'VIEW'
    assert table.primary_key() == []
    table.table_type = 'BASE TABLE'
    assert table.primary_is_composite() is False
    assert len(table.get_primary_columns()) == 1
    primary_columns = table.get_primary_columns()
    assert primary_columns[0].name == 'id'
    assert len(table.get_secondary_columns()) == 2

    # test in ABC order
    secondary_columns = table.get_secondary_columns(sort_results=True)
    assert secondary_columns[0].name == 'name'
    assert secondary_columns[1].name == 'test'

    separated_columns = table.sort_and_separate_columns(separate_nullable=True, separate_primary_key=True)
    assert len(separated_columns.nullable) == 1
    assert len(separated_columns.primary_keys) == 1
    assert len(separated_columns.non_nullable) == 1
    assert len(separated_columns.remaining) == 0

    # test sorting without separation
    separated_columns = table.sort_and_separate_columns()
    assert len(separated_columns.nullable) == 0
    assert len(separated_columns.primary_keys) == 0
    assert len(separated_columns.non_nullable) == 0
    assert len(separated_columns.remaining) == 3
    assert separated_columns.remaining[0].name == 'id'
    assert separated_columns.remaining[1].name == 'name'
    assert separated_columns.remaining[2].name == 'test'
