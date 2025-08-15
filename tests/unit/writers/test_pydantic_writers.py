from dataclasses import dataclass
import pytest

from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.marshalers.schema import get_table_details_from_columns
from supabase_pydantic.db.models import ColumnInfo, ConstraintInfo, RelationshipInfo, TableInfo, ForeignKeyInfo
from supabase_pydantic.core.constants import WriterClassType
from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.core.writers.pydantic import PydanticFastAPIClassWriter, PydanticFastAPIWriter
from supabase_pydantic.utils.types import get_pydantic_type


@pytest.fixture
def relationship_test_tables():
    # Create tables with various relationship types
    post_table = TableInfo(
        name='Post',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='title', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            ColumnInfo(name='author_id', post_gres_datatype='integer', is_nullable=False, datatype='int'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='Post_author_id_fkey',
                column_name='author_id',
                foreign_table_name='User',
                foreign_column_name='id',
                relation_type=RelationType.ONE_TO_ONE,  # Each post has one author
            ),
        ],
        relationships=[
            RelationshipInfo(
                table_name='Post',
                related_table_name='Tag',
                relation_type=RelationType.MANY_TO_MANY,  # Posts can have many tags
            ),
        ],
    )

    user_table = TableInfo(
        name='User',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
        ],
        relationships=[
            RelationshipInfo(
                table_name='User',
                related_table_name='Post',
                relation_type=RelationType.ONE_TO_MANY,  # One user has many posts
            ),
        ],
    )

    tag_table = TableInfo(
        name='Tag',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
        ],
        relationships=[
            RelationshipInfo(
                table_name='Tag',
                related_table_name='Post',
                relation_type=RelationType.MANY_TO_MANY,  # Tags can have many posts and vice versa
            ),
        ],
    )

    post_tag_table = TableInfo(
        name='PostTag',
        schema='public',
        columns=[
            ColumnInfo(name='post_id', post_gres_datatype='integer', is_nullable=False, datatype='int'),
            ColumnInfo(name='tag_id', post_gres_datatype='integer', is_nullable=False, datatype='int'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='PostTag_post_id_fkey',
                column_name='post_id',
                foreign_table_name='Post',
                foreign_column_name='id',
                relation_type=RelationType.MANY_TO_MANY,
            ),
            ForeignKeyInfo(
                constraint_name='PostTag_tag_id_fkey',
                column_name='tag_id',
                foreign_table_name='Tag',
                foreign_column_name='id',
                relation_type=RelationType.MANY_TO_MANY,
            ),
        ],
    )

    return [post_table, user_table, tag_table, post_tag_table]


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


def test_PydanticFastAPIClassWriter_write_name(table_info):
    """Validate the write_name method for Pydantic FastAPI Class Writer."""
    # Test base schema
    base_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.BASE)
    assert base_writer.write_name() == 'UserBaseSchema'

    # Test insert schema
    insert_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.INSERT)
    assert insert_writer.write_name() == 'UserInsert'

    # Test update schema
    update_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.UPDATE)
    assert update_writer.write_name() == 'UserUpdate'


def test_PydanticFastAPIClassWriter_write_metaclass(table_info):
    """Validate the write_metaclass method for Pydantic FastAPI Class Writer."""
    # Test base schema
    base_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.BASE)
    assert base_writer.write_metaclass(['foo', 'bar']) == 'foo, bar'
    assert base_writer.write_metaclass(None) == 'CustomModel'

    # Test insert schema
    insert_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.INSERT)
    assert insert_writer.write_metaclass(None) == 'CustomModelInsert'

    # Test update schema
    update_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.UPDATE)
    assert update_writer.write_metaclass(None) == 'CustomModelUpdate'


def test_PydanticFastAPIClassWriter_write_column(fastapi_class_writer):
    """Validate the write_column method for Pydantic FastAPI Class Writer."""
    column = ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int')
    column_two = ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str', alias='foo')

    expected_output = 'id: int'
    expected_output_two = 'email: str | None = Field(default=None, alias="foo")'

    assert fastapi_class_writer.write_column(column) == expected_output
    assert fastapi_class_writer.write_column(column_two) == expected_output_two


def test_PydanticFastAPIClassWriter_write_class_base(table_info):
    """Validate the write_class method for Pydantic FastAPI Class Writer (BaseSchema)."""
    # Test base schema
    base_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.BASE)
    base_output = (
        'class UserBaseSchema(CustomModel):\n'
        '\t"""User Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int\n\n'
        '\t# Columns\n'
        '\tcompany_id: UUID\n'
        '\temail: str | None = Field(default=None)'
    )
    assert base_writer.write_class() == base_output


def test_PydanticFastAPIClassWriter_write_class_insert(table_info):
    """Validate the write_class method for Pydantic FastAPI Class Writer (Insert)."""
    # Test insert schema
    insert_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.INSERT)
    insert_output = (
        'class UserInsert(CustomModelInsert):\n'
        '\t"""User Insert Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int\n\n'
        '\t# Field properties:\n'
        '\t# email: nullable\n\t\n'
        '\t# Required fields\n'
        '\tcompany_id: UUID\n\t\n'
        '\t\t# Optional fields\n'
        '\temail: str | None = Field(default=None)'
    )
    assert insert_writer.write_class() == insert_output


def test_PydanticFastAPIClassWriter_write_class_update(table_info):
    """Validate the write_class method for Pydantic FastAPI Class Writer (Update)."""
    # Test update schema
    update_writer = PydanticFastAPIClassWriter(table_info, WriterClassType.UPDATE)
    update_output = (
        'class UserUpdate(CustomModelUpdate):\n'
        '\t"""User Update Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int | None = Field(default=None)\n\n'
        '\t# Field properties:\n'
        '\t# email: nullable\n\t\n'
        '\t\t# Optional fields\n'
        '\tcompany_id: UUID | None = Field(default=None)\n'
        '\temail: str | None = Field(default=None)'
    )
    assert update_writer.write_class() == update_output


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
    expected_output = '\t# Foreign Keys\n\tcompany: Company | None = Field(default=None)'
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
        '\tcompany: Company | None = Field(default=None)'
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
        # Imports
        'from __future__ import annotations\n'
        'from pydantic import BaseModel\n'
        'from pydantic import Field\n'
        'from pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from pydantic.types import StringConstraints\n'
        'from typing import Any\n\n\n'
        # Custom Classes
        '# CUSTOM CLASSES\n'
        '# Note: These are custom model classes for defining common features among\n'
        '# Pydantic Base Schema.\n\n\n'
        'class CustomModel(BaseModel):\n'
        '\t"""Base model class with common features."""\n'
        '\tpass\n\n\n'
        'class CustomModelInsert(CustomModel):\n'
        '\t"""Base model for insert operations with common features."""\n'
        '\tpass\n\n\n'
        'class CustomModelUpdate(CustomModel):\n'
        '\t"""Base model for update operations with common features."""\n'
        '\tpass\n\n\n'
        # Base Classes
        '# BASE CLASSES\n'
        '# Note: These are the base Row models that include all fields.\n\n\n'
        'class UserBaseSchema(CustomModel):\n'
        '\t"""User Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int\n\n'
        '\t# Columns\n'
        '\tclient_id: UUID\n'
        '\tcompany_id: UUID\n'
        '\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyBaseSchema(CustomModel):\n'
        '\t"""Company Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID\n\n'
        '\t# Columns\n'
        '\tname: str\n\n\n'
        'class ClientBaseSchema(CustomModel):\n'
        '\t"""Client Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID\n\n'
        '\t# Columns\n'
        '\tinfo_json: dict | None = Field(default=None)\n'
        '\tname: str\n'
        # Insert Classes
        '# INSERT CLASSES\n'
        '# Note: These models are used for insert operations. Auto-generated fields\n'
        '# (like IDs and timestamps) are optional.\n\n\n'
        'class UserInsert(CustomModelInsert):\n'
        '\t"""User Insert Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int\n\n'
        '\t# Field properties:\n'
        '\t# email: nullable\n\t\n'
        '\t# Required fields\n'
        '\tclient_id: UUID\n'
        '\tcompany_id: UUID\n\t\n'
        '\t\t# Optional fields\n'
        '\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyInsert(CustomModelInsert):\n'
        '\t"""Company Insert Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID\n\n'
        '# Required fields\n'
        '\tname: str\n\n\n'
        'class ClientInsert(CustomModelInsert):\n'
        '\t"""Client Insert Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID\n\n'
        '\t# Field properties:\n'
        '\t# info_json: nullable\n\t\n'
        '\t# Required fields\n'
        '\tname: str\n\t\n'
        '\t\t# Optional fields\n'
        '\tinfo_json: dict | None = Field(default=None)\n'
        # Update Classes
        '# UPDATE CLASSES\n'
        '# Note: These models are used for update operations. All fields are optional.\n\n\n'
        'class UserUpdate(CustomModelUpdate):\n'
        '\t"""User Update Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: int | None = Field(default=None)\n\n'
        '\t# Field properties:\n'
        '\t# email: nullable\n\t\n'
        '\t\t# Optional fields\n'
        '\tclient_id: UUID | None = Field(default=None)\n'
        '\tcompany_id: UUID | None = Field(default=None)\n'
        '\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyUpdate(CustomModelUpdate):\n'
        '\t"""Company Update Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID | None = Field(default=None)\n\n'
        '\t# Optional fields\n'
        '\tname: str | None = Field(default=None)\n\n\n'
        'class ClientUpdate(CustomModelUpdate):\n'
        '\t"""Client Update Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID | None = Field(default=None)\n\n'
        '\t# Field properties:\n'
        '\t# info_json: nullable\n\t\n'
        '\t\t# Optional fields\n'
        '\tinfo_json: dict | None = Field(default=None)\n'
        '\tname: str | None = Field(default=None)\n\n\n'
        # Operational Classes
        '# OPERATIONAL CLASSES\n\n\n'
        'class User(UserBaseSchema):\n'
        '\t"""User Schema for Pydantic.\n\n'
        '\tInherits from UserBaseSchema. Add any customization here.\n'
        '\t"""\n\n'
        '\t# Foreign Keys\n'
        '\tcompany: Company | None = Field(default=None)\n'
        '\tclient: Client | None = Field(default=None)\n\n\n'
        'class Company(CompanyBaseSchema):\n'
        '\t"""Company Schema for Pydantic.\n\n'
        '\tInherits from CompanyBaseSchema. Add any customization here.\n'
        '\t"""\n'
        '\tpass\n\n\n'
        'class Client(ClientBaseSchema):\n'
        '\t"""Client Schema for Pydantic.\n\n'
        '\tInherits from ClientBaseSchema. Add any customization here.\n'
        '\t"""\n'
        '\tpass\n'
    )

    assert fastapi_file_writer.write() == expected_output


def test_PydanticFastAPIWriter_write_imports(fastapi_file_writer):
    """Validate the imports for the Pydantic FastAPI writer."""
    expected_imports = (
        'from __future__ import annotations\n'
        'from pydantic import BaseModel\n'
        'from pydantic import Field\n'
        'from pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from pydantic.types import StringConstraints\n'
        'from typing import Any'
    )
    assert fastapi_file_writer.write_imports() == expected_imports


@pytest.fixture
def fastapi_file_writer_with_enum_tables():
    tables = [
        TableInfo(
            name='State',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
                ColumnInfo(
                    name='us_state',
                    post_gres_datatype='USER-DEFINED',
                    is_nullable=False,
                    datatype='us_state',
                    user_defined_values=['CA', 'NY', 'TX', 'IN'],
                    enum_info=EnumInfo(name='us_state', values=['CA', 'NY', 'TX', 'IN'], schema='public'),
                ),
            ],
        ),
        TableInfo(
            name='Country',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
                ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            ],
        ),
    ]
    return PydanticFastAPIWriter(tables, 'dummy_path.py')


def test_PydanticFastAPIWriter_enum_generation(fastapi_file_writer_with_enum_tables):
    """
    Integration test for enum generation in PydanticFastAPIWriter.
    Verifies that enums are generated when enabled, and omitted when disabled.
    """
    # Test with enums enabled
    output_with_enums = fastapi_file_writer_with_enum_tables.write()
    assert 'class UsStateEnum' not in output_with_enums
    assert 'class PublicUsStateEnum' in output_with_enums
    assert 'us_state: PublicUsStateEnum' in output_with_enums

    # Test with enums disabled
    writer_with_no_enums = PydanticFastAPIWriter(
        fastapi_file_writer_with_enum_tables.tables, 'dummy_path.py', generate_enums=False
    )
    output_no_enums = writer_with_no_enums.write()
    assert 'class PublicUsStateEnum' not in output_no_enums
    assert 'us_state: str' in output_no_enums


def test_pluralization_in_relationships():
    """Test that field names are correctly pluralized for many relationships.

    This test verifies that:
    1. Regular nouns are pluralized correctly (e.g., book -> books)
    2. Irregular nouns are pluralized correctly (e.g., child -> children)
    3. Words ending in 'y' are pluralized correctly (e.g., category -> categories)
    4. Already plural words remain plural (e.g., news -> news)
    """
    # Create tables with various column names
    tables = [
        TableInfo(
            name='Book',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ],
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='book_category_id_fkey',
                    column_name='category_id',  # Regular plural: categories
                    foreign_table_name='Category',
                    foreign_column_name='id',
                    relation_type=RelationType.MANY_TO_MANY,
                ),
                ForeignKeyInfo(
                    constraint_name='book_child_id_fkey',
                    column_name='child_id',  # Irregular plural: children
                    foreign_table_name='Child',
                    foreign_column_name='id',
                    relation_type=RelationType.MANY_TO_MANY,
                ),
                ForeignKeyInfo(
                    constraint_name='book_news_id_fkey',
                    column_name='news_id',  # Already plural: news
                    foreign_table_name='News',
                    foreign_column_name='id',
                    relation_type=RelationType.MANY_TO_MANY,
                ),
            ],
        ),
    ]

    # Create writer for the Book table
    book_writer = PydanticFastAPIClassWriter(tables[0])

    # Test pluralization in foreign columns
    book_foreign_cols = book_writer.write_foreign_columns()
    assert 'categories: list[Category] | None = Field(default=None)' in book_foreign_cols
    assert 'children: list[Child] | None = Field(default=None)' in book_foreign_cols
    assert 'news: list[News] | None = Field(default=None)' in book_foreign_cols


def test_relationship_type_handling(relationship_test_tables):
    """Test that foreign key relationships are correctly typed based on their relationship type.

    This test verifies:
    1. ONE_TO_ONE relationships generate a single instance type (e.g., author: User | None)
    2. ONE_TO_MANY relationships generate a list type (e.g., posts: list[Post] | None)
    3. MANY_TO_MANY relationships generate a list type (e.g., tags: list[Tag] | None)
    """
    # Create writers for each table
    post_writer = PydanticFastAPIClassWriter(next(t for t in relationship_test_tables if t.name == 'Post'))
    user_writer = PydanticFastAPIClassWriter(next(t for t in relationship_test_tables if t.name == 'User'))
    tag_writer = PydanticFastAPIClassWriter(next(t for t in relationship_test_tables if t.name == 'Tag'))

    # Test Post model foreign keys and relationships
    post_foreign_cols = post_writer.write_foreign_columns()
    assert 'user: User | None = Field(default=None)' in post_foreign_cols  # ONE_TO_ONE with User
    assert 'tags: list[Tag] | None = Field(default=None)' in post_foreign_cols  # MANY_TO_MANY with Tag

    # Test User model relationships
    user_foreign_cols = user_writer.write_foreign_columns()
    assert 'posts: list[Post] | None = Field(default=None)' in user_foreign_cols  # ONE_TO_MANY with Post

    # Test Tag model relationships
    tag_foreign_cols = tag_writer.write_foreign_columns()
    assert 'posts: list[Post] | None = Field(default=None)' in tag_foreign_cols  # MANY_TO_MANY with Post


def test_relationship_type_edge_cases(relationship_test_tables):
    """Test edge cases in relationship type handling."""
    # Create a table with circular dependencies
    employee_table = TableInfo(
        name='Employee',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            ColumnInfo(name='manager_id', post_gres_datatype='integer', is_nullable=True, datatype='int'),
        ],
        foreign_keys=[
            ForeignKeyInfo(
                constraint_name='Employee_manager_id_fkey',
                column_name='manager_id',
                foreign_table_name='Employee',  # Self-referential
                foreign_column_name='id',
                relation_type=RelationType.ONE_TO_ONE,
            ),
        ],
        relationships=[
            RelationshipInfo(
                table_name='Employee',
                related_table_name='Employee',
                relation_type=RelationType.ONE_TO_MANY,  # One manager has many employees
            ),
        ],
    )

    writer = PydanticFastAPIClassWriter(employee_table)
    foreign_cols = writer.write_foreign_columns()

    # Test self-referential relationships
    assert 'employee: Employee | None = Field(default=None)' in foreign_cols  # ONE_TO_ONE with self
    assert 'employees: list[Employee] | None = Field(default=None)' in foreign_cols  # ONE_TO_MANY with self


def test_relationship_type_error_handling(relationship_test_tables):
    """Test error handling in relationship type handling."""
    # Create a table with invalid relationship type
    invalid_table = TableInfo(
        name='Invalid',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
        ],
        relationships=[
            RelationshipInfo(
                table_name='Invalid',
                related_table_name='NonExistent',  # Table doesn't exist
                relation_type=RelationType.ONE_TO_MANY,
            ),
        ],
    )

    writer = PydanticFastAPIClassWriter(invalid_table)
    foreign_cols = writer.write_foreign_columns()

    # Should not raise an error, just skip the invalid relationship
    assert foreign_cols is None or 'NonExistent' not in foreign_cols


def test_conditional_annotated_import():
    """Test that Annotated is only imported when string constraints are present.

    This test verifies:
    1. When there are columns with text type and length constraints, 'from typing import Annotated' is included
    2. When there are text columns with constraints but no length functions, 'Annotated' is not included
    3. When there are no constraints at all, 'Annotated' is not included
    """
    # Case 1: Table with string length constraints - should trigger Annotated import
    table_with_length_constraints = TableInfo(
        name='Product',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(
                name='sku',
                post_gres_datatype='text',
                is_nullable=False,
                datatype='str',
                constraint_definition='CHECK (length(sku) = 10)',
            ),
        ],
    )

    # Case 2: Table with text columns and constraints, but no length function
    table_with_other_constraints = TableInfo(
        name='Article',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(
                name='title',
                post_gres_datatype='text',
                is_nullable=False,
                datatype='str',
                constraint_definition="CHECK (title <> '')",
            ),
        ],
    )

    # Case 3: Table with no constraints at all
    table_without_constraints = TableInfo(
        name='Simple',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            ColumnInfo(name='active', post_gres_datatype='boolean', is_nullable=True, datatype='bool'),
        ],
    )

    # Test case 1: With string length constraints - should include Annotated import
    writer_with_length = PydanticFastAPIWriter([table_with_length_constraints], 'test_length_constraints.py')
    imports_with_length = writer_with_length.write_imports()
    assert 'from typing import Annotated' in imports_with_length

    # Test case 2: With text constraints but no length function - should NOT include Annotated
    writer_with_other = PydanticFastAPIWriter([table_with_other_constraints], 'test_other_constraints.py')
    imports_with_other = writer_with_other.write_imports()
    assert 'from typing import Annotated' not in imports_with_other

    # Test case 3: Without any constraints - should NOT include Annotated import
    writer_without = PydanticFastAPIWriter([table_without_constraints], 'test_no_constraints.py')
    imports_without = writer_without.write_imports()
    assert 'from typing import Annotated' not in imports_without

    # Test mixed case: Tables with and without constraints
    writer_mixed = PydanticFastAPIWriter([table_with_length_constraints, table_without_constraints], 'test_mixed.py')
    imports_mixed = writer_mixed.write_imports()
    # Should include Annotated because at least one table has length constraints
    assert 'from typing import Annotated' in imports_mixed


def test_enum_array_typing():
    """Test that enum array columns are properly typed in Pydantic models.

    This test verifies:
    1. Regular array columns are typed as list[Type] (e.g., text[] -> list[str])
    2. Enum array columns are typed as list[EnumClass] (e.g., MyEnum[] -> list[PublicMyenumEnum])
    3. Nullable handling is correct for both types
    """

    @dataclass
    class TestEnumInfo:
        """Mock enum info for testing."""

        name: str
        values: list[str]

        def python_class_name(self):
            """Return the Python class name for this enum."""
            return f'Public{self.name.capitalize()}Enum'

    def create_test_column(name, datatype, is_nullable=False, enum_info=None, is_primary=False):
        """Helper function to create test columns."""

        # Convert PostgreSQL type to Pydantic type
        pydantic_type = get_pydantic_type(datatype)[0]

        return ColumnInfo(
            name=name,
            post_gres_datatype=datatype,
            datatype=pydantic_type,  # Use converted Pydantic type
            is_nullable=is_nullable,
            is_identity=False,
            enum_info=enum_info,
            primary=is_primary,
        )

    # Create a test table with enum array fields
    table = TableInfo(
        name='test_table',
        columns=[
            create_test_column('id', 'bigint', is_nullable=False, is_primary=True),
            create_test_column('single_string_field', 'text', is_nullable=True),
            create_test_column(
                'single_enum_field',
                'MyEnum',
                is_nullable=True,
                enum_info=TestEnumInfo('myenum', ['ValueA', 'ValueB', 'ValueC']),
            ),
            create_test_column('my_string_field', 'text[]', is_nullable=True),
            create_test_column(
                'my_enum_field',
                'MyEnum[]',
                is_nullable=True,
                enum_info=TestEnumInfo('myenum', ['ValueA', 'ValueB', 'ValueC']),
            ),
            create_test_column('non_nullable_string_field', 'text[]', is_nullable=False),
            create_test_column(
                'non_nullable_enum_field',
                'MyEnum[]',
                is_nullable=False,
                enum_info=TestEnumInfo('myenum', ['ValueA', 'ValueB', 'ValueC']),
            ),
        ],
        foreign_keys=[],
        constraints=[],
    )

    # Generate model
    writer = PydanticFastAPIClassWriter(table, generate_enums=True)
    model_code = writer.write_class()

    # Verify that array types are correctly typed
    assert 'my_string_field: list[str] | None' in model_code
    assert 'my_enum_field: list[PublicMyenumEnum] | None' in model_code
    assert 'non_nullable_string_field: list[str]' in model_code
    assert 'non_nullable_enum_field: list[PublicMyenumEnum]' in model_code

    # Verify that regular (non-array) fields are still properly typed
    assert 'single_string_field: str | None' in model_code
    assert 'single_enum_field: PublicMyenumEnum | None' in model_code


def test_enum_array_in_pydantic_model():
    """Test that enum arrays are correctly typed in Pydantic models."""
    # Create mock column data
    mock_column_data = [
        (
            'public',
            'test_table',
            'status_array',
            None,
            'YES',
            'ARRAY',
            None,
            'BASE TABLE',
            None,
            '_test_status',
            'test_status[]',
        ),
        ('public', 'test_table', 'status', None, 'YES', 'USER-DEFINED', None, 'BASE TABLE', None, 'test_status', None),
    ]

    # Process mock data
    tables = get_table_details_from_columns(mock_column_data)
    table = tables[('public', 'test_table')]

    # Find columns
    array_column = None
    scalar_column = None
    for col in table.columns:
        if col.name == 'status_array':
            array_column = col
        elif col.name == 'status':
            scalar_column = col

    # Create enum info
    enum_info = EnumInfo(name='test_status', values=['active', 'pending', 'inactive'], schema='public')

    # Apply enum info to columns
    array_column.enum_info = enum_info
    scalar_column.enum_info = enum_info

    # Create class writer for column handling
    class_writer = PydanticFastAPIClassWriter(table, generate_enums=True)

    # Generate field code for both columns
    array_field_code = class_writer.write_column(array_column)
    scalar_field_code = class_writer.write_column(scalar_column)

    # Verify the array is typed properly with the enum class
    assert 'list[PublicTestStatusEnum]' in array_field_code, 'Array field not typed correctly with enum class'
    assert 'PublicTestStatusEnum' in scalar_field_code, 'Scalar field not typed correctly with enum class'
