import pytest
from supabase_pydantic.util.constants import RelationType
from supabase_pydantic.util.dataclasses import ConstraintInfo, ForeignKeyInfo, TableInfo, ColumnInfo
from supabase_pydantic.util.writers.pydantic_writers import (
    PydanticFastAPIClassWriter,
    PydanticFastAPIWriter,
)


@pytest.fixture
def table_info():
    return TableInfo(
        name='User',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str'),
            ColumnInfo(name='company_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='User_company_id_fkey',
                column_name='company_id',
                foreign_table_name='Company',
                foreign_column_name='id',
                relation_type=RelationType.ONE_TO_ONE,
            ),
        ],
        constraints=[
            ConstraintInfo(
                constraint_name='User_pkey',
                raw_constraint_type='p',
                columns=['id'],
                constraint_definition='PRIMARY KEY (id)',
            ),
        ],
    )


@pytest.fixture
def fastapi_class_writer(table_info):
    return PydanticFastAPIClassWriter(table_info)


@pytest.fixture
def api_writer_tables():
    return [
        TableInfo(
            name='User',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
                ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str'),
                ColumnInfo(name='company_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID'),
                ColumnInfo(name='client_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID'),
            ],
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='User_company_id_fkey',
                    column_name='company_id',
                    foreign_table_name='Company',
                    foreign_column_name='id',
                    relation_type=RelationType.ONE_TO_ONE,
                ),
                ForeignKeyInfo(
                    constraint_name='User_client_id_fkey',
                    column_name='client_id',
                    foreign_table_name='Client',
                    foreign_column_name='id',
                    relation_type=RelationType.ONE_TO_ONE,
                ),
            ],
            constraints=[
                ConstraintInfo(
                    constraint_name='User_pkey',
                    raw_constraint_type='p',
                    columns=['id'],
                    constraint_definition='PRIMARY KEY (id)',
                ),
            ],
        ),
        TableInfo(
            name='Company',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='uuid', is_nullable=False, primary=True, datatype='UUID'),
                ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            ],
            foreign_keys=[],
            constraints=[
                ConstraintInfo(
                    constraint_name='Company_pkey',
                    raw_constraint_type='p',
                    columns=['id'],
                    constraint_definition='PRIMARY KEY (id)',
                ),
            ],
        ),
        TableInfo(
            name='Client',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='uuid', is_nullable=False, primary=True, datatype='UUID'),
                ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
                ColumnInfo(name='info_json', post_gres_datatype='jsonb', is_nullable=True, datatype='dict'),
            ],
            foreign_keys=[],
            constraints=[
                ConstraintInfo(
                    constraint_name='Client_pkey',
                    raw_constraint_type='p',
                    columns=['id'],
                    constraint_definition='PRIMARY KEY (id)',
                ),
            ],
        ),
    ]


@pytest.fixture
def fastapi_file_writer(api_writer_tables):
    return PydanticFastAPIWriter(api_writer_tables, 'dummy_path.py')


def test_PydanticFastAPIClassWriter_write_name(fastapi_class_writer):
    """Validate the write_name method for Pydantic FastAPI Class Writer."""
    assert fastapi_class_writer.write_name() == 'UserBaseSchema'


def test_PydanticFastAPIClassWriter_write_metaclass(fastapi_class_writer):
    """Validate the write_metaclass method for Pydantic FastAPI Class Writer."""
    expected_output = 'foo, bar'
    assert fastapi_class_writer.write_metaclass(['foo', 'bar']) == expected_output
    assert fastapi_class_writer.write_metaclass(None) == 'CustomModel'


def test_PydanticFastAPIClassWriter_write_column(fastapi_class_writer):
    """Validate the write_column method for Pydantic FastAPI Class Writer."""
    column = ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int')
    column_two = ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str', alias='foo')

    expected_output = 'id: int'
    expected_output_two = 'email: str | None = Field(default=None, alias="foo")'

    assert fastapi_class_writer.write_column(column) == expected_output
    assert fastapi_class_writer.write_column(column_two) == expected_output_two


def test_PydanticFastAPIClassWriter_write_class(fastapi_class_writer):
    """Validate the write_class method for Pydantic FastAPI Class Writer."""
    expected_output = (
        'class UserBaseSchema(CustomModel):\n'
        '\t"""User Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int\n\n'
        '\t# Columns\n'
        '\tcompany_id: UUID4\n'
        '\temail: str | None = Field(default=None)'
    )
    assert fastapi_class_writer.write_class() == expected_output


def test_PydanticFastAPIClassWriter_write_primary_keys_no_columns():
    """Validate the write_primary_keys method for Pydantic FastAPI Class Writer."""
    table_info = TableInfo(name='User', schema='public', columns=[], foreign_keys=[], constraints=[])
    writer = PydanticFastAPIClassWriter(table_info)
    expected_output = 'class UserBaseSchema(CustomModel):\n\t"""User Base Schema."""\n\n'
    assert writer.write_class() == expected_output


def test_PydanticFastAPIClassWriter_write_foreign_columns_basic():
    """Test that write_foreign_columns correctly generates foreign key fields.

    This test verifies:
    1. A single foreign key relationship is correctly written as a Field
    2. Empty foreign keys list returns None
    """
    table_info = TableInfo(
        name='User',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str'),
            ColumnInfo(
                name='company_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID', is_foreign_key=True
            ),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                column_name='company_id',
                foreign_table_name='Company',
                foreign_column_name='id',
                relation_type=RelationType.ONE_TO_ONE,
                foreign_table_schema='public',
                constraint_name='User_company_id_fkey',
            )
        ],
        constraints=[],
    )

    writer = PydanticFastAPIClassWriter(table_info)
    expected_output = '\t# Foreign Keys\n\tcompany: list[Company] | None = Field(default=None)'
    assert writer.write_foreign_columns() == expected_output

    table_info.foreign_keys = []
    new_writer = PydanticFastAPIClassWriter(table_info)
    assert new_writer.write_foreign_columns() is None


def test_PydanticFastAPIClassWriter_write_foreign_columns_no_foreign_keys():
    """Test that write_foreign_columns returns None when there are no foreign keys.

    This test specifically verifies that even with a foreign key column,
    if there are no foreign key constraints defined, the method returns None.
    """
    table_info = TableInfo(
        name='User',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str'),
            ColumnInfo(
                name='company_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID', is_foreign_key=True
            ),
        ],
        foreign_keys=[],
        constraints=[
            ConstraintInfo(
                constraint_name='User_pkey',
                raw_constraint_type='p',
                columns=['id'],
                constraint_definition='PRIMARY KEY (id)',
            ),
        ],
    )
    writer = PydanticFastAPIClassWriter(table_info)
    assert writer.write_foreign_columns() is None


def test_PydanticFastAPIClassWriter_write_operational_class_with_foreign_keys(table_info):
    """Test that write_operational_class correctly includes foreign key relationships.

    This test verifies:
    1. The complete operational class is generated with proper inheritance
    2. Foreign key relationships are included in the class body
    3. When foreign keys are removed, the class is generated with a pass statement
    """
    writer = PydanticFastAPIClassWriter(table_info)
    expected_output = (
        'class User(UserBaseSchema):\n\t'
        '"""User Schema for Pydantic.\n\n\t'
        'Inherits from UserBaseSchema. Add any customization here.\n\t"""\n\n'
        '\t# Foreign Keys\n'
        '\tcompany: list[Company] | None = Field(default=None)'
    )
    assert writer.write_operational_class() == expected_output

    table_info.foreign_keys = []
    expected_output = (
        'class User(UserBaseSchema):\n\t'
        '"""User Schema for Pydantic.\n\n\t'
        'Inherits from UserBaseSchema. Add any customization here.\n\t"""\n'
        '\tpass'
    )


def test_PydanticFastAPIWriter_write(fastapi_file_writer):
    """Validate the write method for Pydantic FastAPI Writer."""
    expected_output = (
        'from __future__ import annotations\nfrom pydantic import Annotated'
        '\nfrom pydantic import BaseModel\nfrom pydantic import Field\nfrom pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from pydantic.types import StringConstraints\n\n\n# CUSTOM CLASSES\n'
        '# Note: This is a custom model class for defining common features among\n'
        '# Pydantic Base Schema.\n\n\nclass CustomModel(BaseModel):\n\tpass\n\n\n'
        '# BASE CLASSES\n\n\n'
        'class UserBaseSchema(CustomModel):\n\t"""User Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: int\n\n\t# Columns\n\tclient_id: UUID4\n\tcompany_id: UUID4'
        '\n\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyBaseSchema(CustomModel):\n\t"""Company Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: UUID4\n\n\t# Columns\n\tname: str\n\n\n'
        'class ClientBaseSchema(CustomModel):\n\t"""Client Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: UUID4\n\n\t# Columns\n\tinfo_json: dict | Json | None = Field(default=None)\n\t'
        'name: str\n\n\n# OPERATIONAL CLASSES\n\n\nc'
        'lass User(UserBaseSchema):\n\t"""User Schema for Pydantic.\n\n\t'
        'Inherits from UserBaseSchema. Add any customization here.\n\t"""\n\n\t'
        '# Foreign Keys\n\tcompany: list[Company] | None = Field(default=None)\n\t'
        'client: list[Client] | None = Field(default=None)\n\n\n'
        'class Company(CompanyBaseSchema):\n\t"""Company Schema for Pydantic.\n\n\t'
        'Inherits from CompanyBaseSchema. Add any customization here.\n\t"""\n\tpass\n\n\n'
        'class Client(ClientBaseSchema):\n\t"""Client Schema for Pydantic.\n\n\t'
        'Inherits from ClientBaseSchema. Add any customization here.\n\t"""\n\tpass\n'
    )

    assert fastapi_file_writer.write() == expected_output


def test_PydanticFastAPIWriter_write_imports(fastapi_file_writer):
    """Validate the imports for the Pydantic FastAPI writer."""
    expected_imports = (
        'from __future__ import annotations\n'
        'from pydantic import Annotated\n'
        'from pydantic import BaseModel\n'
        'from pydantic import Field\n'
        'from pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from pydantic.types import StringConstraints'
    )
    assert fastapi_file_writer.write_imports() == expected_imports
