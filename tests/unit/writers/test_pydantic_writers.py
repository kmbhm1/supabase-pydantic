import pytest
from supabase_pydantic.util.constants import RelationType
from supabase_pydantic.util.dataclasses import ConstraintInfo, ForeignKeyInfo
from supabase_pydantic.util.writers.pydantic_writers import (
    PydanticFastAPIClassWriter,
    PydanticFastAPIWriter,
    PydanticJSONAPIClassWriter,
    PydanticJSONAPIWriter,
    TableInfo,
    ColumnInfo,
)


# Sample TableInfo setup
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
def jsonapi_class_writer(table_info):
    return PydanticJSONAPIClassWriter(table_info)


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


@pytest.fixture
def jsonapi_writer(api_writer_tables):
    return PydanticJSONAPIWriter(api_writer_tables, 'dummy_path.py')


def test_pydantic_fast_api_writer_imports(fastapi_file_writer):
    """Validate the imports for the Pydantic FastAPI writer."""
    expected_imports = (
        'from __future__ import annotations\n'
        'from pydantic import BaseModel\n'
        'from pydantic import Field\n'
        'from pydantic import Json\n'
        'from pydantic import UUID4'
    )
    assert fastapi_file_writer.write_imports() == expected_imports


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
    expected_output = 'class UserBaseSchema(CustomModel):\n' '\t"""User Base Schema."""\n\n'
    assert writer.write_class() == expected_output


def test_PydanticFastAPIClassWriter_write_foreign_columns():
    """Validate the write_foreign_columns method for Pydantic FastAPI Class Writer."""
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
    writer = PydanticFastAPIClassWriter(table_info)
    expected_output = '\t# Foreign Keys\n\tcompany: list[Company] | None = Field(default=None)'
    assert writer.write_foreign_columns() == expected_output

    table_info.foreign_keys = []
    new_writer = PydanticFastAPIClassWriter(table_info)
    assert new_writer.write_foreign_columns() is None


def test_PydanticFastAPIClassWriter_write_foreign_columns_returns_None():
    """Validate the write_foreign_columns method for Pydantic FastAPI Class Writer returns None with no foreign tables."""
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


def test_PydanticFastAPIClassWriter_write_foreign_columns(table_info):
    """Validate the write_foreign_columns method for Pydantic FastAPI Class Writer."""
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
        'from __future__ import annotations\nfrom pydantic import BaseModel\n'
        'from pydantic import Field\nfrom pydantic import Json\n'
        'from pydantic import UUID4\n\n\n############################## Custom Classes\n'
        '# Note: This is a custom model class for defining common features among\n'
        '# Pydantic Base Schema.\n\n\nclass CustomModel(BaseModel):\n\tpass\n\n\n'
        '############################## Base Classes\n\n\n'
        'class UserBaseSchema(CustomModel):\n\t"""User Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: int\n\n\t# Columns\n\tclient_id: UUID4\n\tcompany_id: UUID4'
        '\n\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyBaseSchema(CustomModel):\n\t"""Company Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: UUID4\n\n\t# Columns\n\tname: str\n\n\n'
        'class ClientBaseSchema(CustomModel):\n\t"""Client Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: UUID4\n\n\t# Columns\n\tinfo_json: dict | Json | None = Field(default=None)\n\t'
        'name: str\n\n\n############################## Operational Classes\n\n\nc'
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


def test_PydanticJSONAPIClassWriter_write(jsonapi_class_writer):
    """Validate the write method for Pydantic JSONAPI Class Writer."""
    expected_output = (
        'class UserBaseSchema(CustomModel):\n\t'
        '"""User Base Schema."""\n\n\t# Primary Keys\n\t'
        'id: int\n\n\t# Columns\n\tcompany_id: UUID4\n\t'
        'email: str | None = Field(default=None)\n\n'
        '\t# Relationships\n\tcompany: CompanyBaseSchema | None = Field('
        '\n\t\trelationsip=RelationshipInfo(\n\t\t\tresource_type="company"'
        '\n\t\t),\n\t)'
    )

    assert jsonapi_class_writer.write_class() == expected_output


def test_PydanticJSONAPIClassWriter_write_foreign_columns_returns_none():
    """Validate the write_foreign_columns method for Pydantic JSONAPI Class Writer returns None with no foreign tables."""
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
    writer = PydanticJSONAPIClassWriter(table_info)
    assert writer.write_foreign_columns() is None


def test_PydanticJSONAPIClassWriter_write_operational_class(jsonapi_class_writer):
    """Validate the write_operational_class method for Pydantic JSONAPI Class Writer."""
    expected_output = (
        'class UserPatchSchema(UserBaseSchema):\n\t'
        '"""User PATCH Schema."""\n\t'
        'pass\n\nclass UserInputSchema(UserBaseSchema):\n\t'
        '"""User INPUT Schema."""\n\tpass\n\n'
        'class UserItemSchema(UserBaseSchema):\n\t"""User ITEM Schema."""'
        '\n\tpass'
    )

    assert jsonapi_class_writer.write_operational_class() == expected_output


def test_PydanticJSONAPIWriter_write(jsonapi_writer):
    """Validate the write method for Pydantic JSONAPI Writer."""
    expected_output = (
        'from __future__ import annotations\n'
        'from fastapi_jsonapi.schema_base import Field, RelationshipInfo\n'
        'from pydantic import BaseModel as PydanticBaseModel\n'
        'from pydantic import Json\nfrom pydantic import UUID4\n\n\n'
        '############################## Custom Classes\n'
        '# Note: This is a custom model class for defining common features among\n'
        '# Pydantic Base Schema.\n\n\nclass CustomModel(PydanticBaseModel):\n\t'
        'pass\n\n\n############################## Base Classes\n\n\n'
        'class UserBaseSchema(CustomModel):\n\t"""User Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: int\n\n\t# Columns\n\tclient_id: UUID4\n\t'
        'company_id: UUID4\n\temail: str | None = Field(default=None)\n\n\t'
        '# Relationships\n\tcompany: CompanyBaseSchema | None = Field(\n\t\t'
        'relationsip=RelationshipInfo(\n\t\t\tresource_type="company"\n\t\t),\n\t)'
        '\n\tclient: ClientBaseSchema | None = Field(\n\t\t'
        'relationsip=RelationshipInfo(\n\t\t\tresource_type="client"\n\t\t),\n\t)\n\n\n'
        'class CompanyBaseSchema(CustomModel):\n\t"""Company Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: UUID4\n\n\t# Columns\n\tname: str\n\n\n'
        'class ClientBaseSchema(CustomModel):\n\t"""Client Base Schema."""\n\n\t'
        '# Primary Keys\n\tid: UUID4\n\n\t# Columns\n\t'
        'info_json: dict | Json | None = Field(default=None)\n\tname: str\n\n\n'
        '############################## Operational Classes\n\n\n'
        'class UserPatchSchema(UserBaseSchema):\n\t"""User PATCH Schema."""\n\tpass'
        '\n\nclass UserInputSchema(UserBaseSchema):\n\t"""User INPUT Schema."""\n\t'
        'pass\n\nclass UserItemSchema(UserBaseSchema):\n\t"""User ITEM Schema."""\n\t'
        'pass\n\n\nclass CompanyPatchSchema(CompanyBaseSchema):\n\t'
        '"""Company PATCH Schema."""\n\tpass\n\n'
        'class CompanyInputSchema(CompanyBaseSchema):\n\t"""Company INPUT Schema."""\n\t'
        'pass\n\nclass CompanyItemSchema(CompanyBaseSchema):\n\t'
        '"""Company ITEM Schema."""\n\tpass\n\n\n'
        'class ClientPatchSchema(ClientBaseSchema):\n\t"""Client PATCH Schema."""\n\t'
        'pass\n\nclass ClientInputSchema(ClientBaseSchema):\n\t"""Client INPUT Schema."""'
        '\n\tpass\n\nclass ClientItemSchema(ClientBaseSchema):\n\t'
        '"""Client ITEM Schema."""\n\tpass\n'
    )

    assert jsonapi_writer.write() == expected_output
