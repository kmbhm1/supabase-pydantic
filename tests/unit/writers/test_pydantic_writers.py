import pytest

from supabase_pydantic.util.constants import RelationType, WriterClassType
from supabase_pydantic.util.dataclasses import ColumnInfo, ConstraintInfo, ForeignKeyInfo, RelationshipInfo, TableInfo
from supabase_pydantic.util.writers.pydantic_writers import PydanticFastAPIClassWriter, PydanticFastAPIWriter


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
        '\tcompany_id: UUID4\n'
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
        '\tcompany_id: UUID4\n\t\n'
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
        '\tcompany_id: UUID4 | None = Field(default=None)\n'
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
    expected_output = '\t# Foreign Keys\n\tcompany_id: Company | None = Field(default=None)'
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
        '\tcompany_id: Company | None = Field(default=None)'
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
        'from pydantic import Annotated\n'
        'from pydantic import BaseModel\n'
        'from pydantic import Field\n'
        'from pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from pydantic.types import StringConstraints\n\n\n'
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
        '\tclient_id: UUID4\n'
        '\tcompany_id: UUID4\n'
        '\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyBaseSchema(CustomModel):\n'
        '\t"""Company Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID4\n\n'
        '\t# Columns\n'
        '\tname: str\n\n\n'
        'class ClientBaseSchema(CustomModel):\n'
        '\t"""Client Base Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID4\n\n'
        '\t# Columns\n'
        '\tinfo_json: dict | Json | None = Field(default=None)\n'
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
        '\tclient_id: UUID4\n'
        '\tcompany_id: UUID4\n\t\n'
        '\t\t# Optional fields\n'
        '\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyInsert(CustomModelInsert):\n'
        '\t"""Company Insert Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID4\n\n'
        '# Required fields\n'
        '\tname: str\n\n\n'
        'class ClientInsert(CustomModelInsert):\n'
        '\t"""Client Insert Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID4\n\n'
        '\t# Field properties:\n'
        '\t# info_json: nullable\n\t\n'
        '\t# Required fields\n'
        '\tname: str\n\t\n'
        '\t\t# Optional fields\n'
        '\tinfo_json: dict | Json | None = Field(default=None)\n'
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
        '\tclient_id: UUID4 | None = Field(default=None)\n'
        '\tcompany_id: UUID4 | None = Field(default=None)\n'
        '\temail: str | None = Field(default=None)\n\n\n'
        'class CompanyUpdate(CustomModelUpdate):\n'
        '\t"""Company Update Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID4 | None = Field(default=None)\n\n'
        '\t# Optional fields\n'
        '\tname: str | None = Field(default=None)\n\n\n'
        'class ClientUpdate(CustomModelUpdate):\n'
        '\t"""Client Update Schema."""\n\n'
        '\t# Primary Keys\n'
        '\tid: UUID4 | None = Field(default=None)\n\n'
        '\t# Field properties:\n'
        '\t# info_json: nullable\n\t\n'
        '\t\t# Optional fields\n'
        '\tinfo_json: dict | Json | None = Field(default=None)\n'
        '\tname: str | None = Field(default=None)\n\n\n'
        # Operational Classes
        '# OPERATIONAL CLASSES\n\n\n'
        'class User(UserBaseSchema):\n'
        '\t"""User Schema for Pydantic.\n\n'
        '\tInherits from UserBaseSchema. Add any customization here.\n'
        '\t"""\n\n'
        '\t# Foreign Keys\n'
        '\tcompany_id: Company | None = Field(default=None)\n'
        '\tclient_id: Client | None = Field(default=None)\n\n\n'
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
        'from pydantic import Annotated\n'
        'from pydantic import BaseModel\n'
        'from pydantic import Field\n'
        'from pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from pydantic.types import StringConstraints'
    )
    assert fastapi_file_writer.write_imports() == expected_imports


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
    assert 'category_ids: list[Category] | None = Field(default=None)' in book_foreign_cols
    assert 'child_ids: list[Child] | None = Field(default=None)' in book_foreign_cols
    assert 'news_ids: list[News] | None = Field(default=None)' in book_foreign_cols


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
    assert 'author_id: User | None = Field(default=None)' in post_foreign_cols  # ONE_TO_ONE with User
    assert 'tag: list[Tag] | None = Field(default=None)' in post_foreign_cols  # MANY_TO_MANY with Tag

    # Test User model relationships
    user_foreign_cols = user_writer.write_foreign_columns()
    assert 'post: list[Post] | None = Field(default=None)' in user_foreign_cols  # ONE_TO_MANY with Post

    # Test Tag model relationships
    tag_foreign_cols = tag_writer.write_foreign_columns()
    assert 'post: list[Post] | None = Field(default=None)' in tag_foreign_cols  # MANY_TO_MANY with Post
