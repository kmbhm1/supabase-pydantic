import pytest

from supabase_pydantic.db.models import ColumnInfo, ConstraintInfo, RelationshipInfo, TableInfo, ForeignKeyInfo
from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.core.writers.sqlalchemy import SqlAlchemyFastAPIClassWriter, SqlAlchemyFastAPIWriter


@pytest.fixture
def table_info():
    """Return a TableInfo instance for testing."""
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
def tables(table_info):
    """Return a list of TableInfo instances for testing."""
    return [
        table_info,
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
def blog_tables():
    """Return a list of TableInfo instances for testing relationships."""
    return [
        TableInfo(
            name='User',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='uuid', is_nullable=False, primary=True, datatype='UUID'),
                ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
                ColumnInfo(name='profile_id', post_gres_datatype='uuid', is_nullable=True, datatype='UUID'),
            ],
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='User_profile_id_fkey',
                    column_name='profile_id',
                    foreign_table_name='Profile',
                    foreign_column_name='id',
                    relation_type=RelationType.ONE_TO_ONE,
                ),
            ],
            relationships=[
                RelationshipInfo(
                    table_name='user',
                    related_table_name='post',
                    relation_type=RelationType.ONE_TO_MANY,
                ),
            ],
        ),
        TableInfo(
            name='Profile',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='uuid', is_nullable=False, primary=True, datatype='UUID'),
                ColumnInfo(name='bio', post_gres_datatype='text', is_nullable=True, datatype='str'),
            ],
            relationships=[
                RelationshipInfo(
                    table_name='profile',
                    related_table_name='user',
                    relation_type=RelationType.ONE_TO_ONE,
                ),
            ],
        ),
        TableInfo(
            name='Post',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='uuid', is_nullable=False, primary=True, datatype='UUID'),
                ColumnInfo(name='title', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
                ColumnInfo(name='author_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID'),
            ],
            foreign_keys=[
                ForeignKeyInfo(
                    constraint_name='Post_author_id_fkey',
                    column_name='author_id',
                    foreign_table_name='User',
                    foreign_column_name='id',
                    relation_type=RelationType.ONE_TO_MANY,
                ),
            ],
            relationships=[
                RelationshipInfo(
                    table_name='post',
                    related_table_name='comment',
                    relation_type=RelationType.ONE_TO_MANY,
                ),
                RelationshipInfo(
                    table_name='post',
                    related_table_name='tag',
                    relation_type=RelationType.MANY_TO_MANY,
                ),
            ],
        ),
    ]


@pytest.fixture
def fastapi_class_writer(table_info):
    """Return a SqlAlchemyFastAPIClassWriter instance."""
    return SqlAlchemyFastAPIClassWriter(table_info)


@pytest.fixture
def fastapi_writer(tables):
    """Return a SqlAlchemyFastAPIWriter instance."""
    return SqlAlchemyFastAPIWriter(tables, 'made-up-file-path.py')


def test_SqlAlchemyFastAPIClassWriter_write_name(fastapi_class_writer):
    """Verify the write_name method returns the expected value."""
    assert fastapi_class_writer.write_name() == 'User'


def test_SqlAlchemyFastAPIClassWriter_write_metaclass_returns_Base(fastapi_class_writer):
    """Verify the write_metaclass method returns the expected value."""
    assert fastapi_class_writer.write_metaclass() == 'Base'
    assert fastapi_class_writer.write_metaclass('foo') == 'Base'


def test_SqlAlchemyFastAPIClassWriter_write_docs(fastapi_class_writer):
    """Verify the write_docs method returns the expected value."""
    assert fastapi_class_writer.write_docs() == '\n\t"""User Base."""\n\n\t__tablename__ = "User"\n'


def test_SqlAlchemyFastAPIClassWriter_write_column(fastapi_class_writer):
    """Verify the write_column method returns expected values."""
    assert (
        fastapi_class_writer.write_column(
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int')
        )
        == 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'
        and fastapi_class_writer.write_column(
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int')
        )
        != 'id = Column(Integer, primary_key=True)'
    )
    assert (
        fastapi_class_writer.write_column(
            ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str')
        )
        == 'email: Mapped[str | None] = mapped_column(String)'
        and fastapi_class_writer.write_column(
            ColumnInfo(name='email', post_gres_datatype='varchar', is_nullable=True, datatype='str')
        )
        != 'email = Column(String, nullable=True)'
    )
    assert (
        fastapi_class_writer.write_column(
            ColumnInfo(name='company_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID')
        )
        == 'company_id: Mapped[UUID4] = mapped_column(UUID(as_uuid=True), ForeignKey("Company.id"))'
        and fastapi_class_writer.write_column(
            ColumnInfo(name='company_id', post_gres_datatype='uuid', is_nullable=False, datatype='UUID')
        )
        != 'company_id = Column(UUID(as_uuid=True), ForeignKey("Company.id"))'
    )
    assert (
        fastapi_class_writer.write_column(
            ColumnInfo(
                name='created_at', post_gres_datatype='timestamp with time zone', is_nullable=False, datatype='datetime'
            )
        )
        == 'created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))'
        and fastapi_class_writer.write_column(
            ColumnInfo(
                name='created_at', post_gres_datatype='timestamp with time zone', is_nullable=False, datatype='datetime'
            )
        )
        != 'created_at = Column(TIMESTAMP(timezone=True))'
    )
    assert (
        fastapi_class_writer.write_column(
            ColumnInfo(
                name='unique_string', post_gres_datatype='varchar', is_nullable=False, is_unique=True, datatype='str'
            )
        )
        == 'unique_string: Mapped[str] = mapped_column(String, unique=True)'
        and fastapi_class_writer.write_column(
            ColumnInfo(
                name='unique_string', post_gres_datatype='varchar', is_nullable=False, is_unique=True, datatype='str'
            )
        )
        != 'unique_string = Column(String, unique=True)'
    )
    assert (
        fastapi_class_writer.write_column(
            ColumnInfo(
                name='data_only',
                post_gres_datatype='jsonb',
                is_nullable=False,
                is_unique=False,
                primary=False,
                datatype='dict',
            )
        )
        == 'data_only: Mapped[dict | Json] = mapped_column(JSONB)'
        and fastapi_class_writer.write_column(
            ColumnInfo(
                name='data_only',
                post_gres_datatype='jsonb',
                is_nullable=False,
                is_unique=False,
                primary=False,
                datatype='dict',
            )
        )
        != 'data_only = Column(JSONB)'
    )


def test_SqlAlchemyFastAPIClassWriter_write_primary_keys(fastapi_class_writer):
    """Verify the write_primary_keys method returns the expected value."""
    assert (
        fastapi_class_writer.write_primary_keys()
        == '\t# Primary Keys\n\tid: Mapped[int] = mapped_column(Integer, primary_key=True)'
    )


def test_SqlAlchemyFastAPIClassWriter_write_foreign_columns(fastapi_class_writer):
    """Verify the write_foreign_columns method returns the expected value."""
    expected_value = "\t# Table Args\n\t__table_args__ = (\n\t\tPrimaryKeyConstraint('id', name='User_pkey'),\n\t\t{ 'schema': 'public' }\n\t)\n\n\t# Relationships\n\tcompany: Mapped[Company | None] = relationship(\"Company\", back_populates=\"users\", uselist=False)\n"
    assert fastapi_class_writer.write_foreign_columns() == expected_value


def test_SqlAlchemyFastAPIClassWriter_write_foreign_columns_relationships(blog_tables):
    """Verify the write_foreign_columns method handles different relationship types correctly."""
    # Test User model (ONE_TO_ONE with Profile, ONE_TO_MANY with Posts)
    user_table = [t for t in blog_tables if t.name == 'User'][0]
    user_writer = SqlAlchemyFastAPIClassWriter(user_table)
    user_foreign_cols = user_writer.write_foreign_columns()

    assert (
        'profile: Mapped[Profile | None] = relationship("Profile", back_populates="users", uselist=False)'
        in user_foreign_cols
    )
    assert 'posts: Mapped[list[Post]] = relationship("Post", back_populates="users")' in user_foreign_cols

    # Test Post model (ONE_TO_MANY with Comments, MANY_TO_MANY with Tags)
    post_table = [t for t in blog_tables if t.name == 'Post'][0]
    post_writer = SqlAlchemyFastAPIClassWriter(post_table)
    post_foreign_cols = post_writer.write_foreign_columns()

    assert 'comments: Mapped[list[Comment]] = relationship("Comment", back_populates="posts")' in post_foreign_cols
    assert 'tags: Mapped[list[Tag]] = relationship("Tag", back_populates="posts")' in post_foreign_cols

    # Test Profile model (ONE_TO_ONE with User)
    profile_table = [t for t in blog_tables if t.name == 'Profile'][0]
    profile_writer = SqlAlchemyFastAPIClassWriter(profile_table)
    profile_foreign_cols = profile_writer.write_foreign_columns()

    assert (
        'user: Mapped[User | None] = relationship("User", back_populates="profiles", uselist=False)'
        in profile_foreign_cols
    )


def test_SqlAlchemyFastAPIClassWriter_write_operational_class_returns_None(fastapi_class_writer):
    """Verify the write_operational_class method returns None."""
    assert fastapi_class_writer.write_operational_class() is None


def test_SqlAlchemyFastAPIClassWriter_write_columns(fastapi_class_writer):
    """Verify the write_columns method returns the expected value."""
    expected_value = (
        '\t# Primary Keys\n\tid: Mapped[int] = mapped_column(Integer, primary_key=True)\n\n\t'
        '# Columns\n\tcompany_id: Mapped[UUID4] = mapped_column(UUID(as_uuid=True), ForeignKey("Company.id"))'
        '\n\temail: Mapped[str | None] = mapped_column(String)\n'
    )
    assert fastapi_class_writer.write_columns() == expected_value


def test_SqlAlchemyFastAPIWriter_write_primary_columns_returns_None_with_no_columns():
    """Verify the write_primary_columns method returns None when there are no columns."""
    new_table_no_columns = TableInfo(
        name='NewTable',
        schema='public',
        columns=[],
        foreign_keys=[],
        constraints=[],
    )
    new_fastapi_class_writer = SqlAlchemyFastAPIClassWriter(new_table_no_columns)
    assert new_fastapi_class_writer.write_primary_columns() is None


def test_SqlAlchemyFastAPIClassWriter_column_section_is_static():
    """Verify the column_section method is static and is correct."""
    assert SqlAlchemyFastAPIClassWriter.column_section('foo', ['bar', 'baz']) == '\t# foo\n\tbar\n\tbaz'


def test_SqlAlchemyFastAPIWriter_write(fastapi_writer):
    """Verify the correct file output is written."""
    expected_value = (
        'from pydantic import Json\n'
        'from pydantic import UUID4\n'
        'from sqlalchemy import ForeignKey\n'
        'from sqlalchemy import Integer\n'
        'from sqlalchemy import PrimaryKeyConstraint\n'
        'from sqlalchemy import String\n'
        'from sqlalchemy.dialects.postgresql import JSONB\n'
        'from sqlalchemy.dialects.postgresql import UUID\n'
        'from sqlalchemy.orm import DeclarativeBase\n'
        'from sqlalchemy.orm import Mapped\n'
        'from sqlalchemy.orm import mapped_column\n'
        'from sqlalchemy.orm import relationship\n\n\n'
        '# DECLARATIVE BASE\n\n\n'
        'class Base(DeclarativeBase):\n'
        '\t"""Declarative Base Class."""\n'
        '\t# type_annotation_map = {}\n\n'
        '\tpass\n\n\n'
        '# BASE CLASSES\n\n\n'
        'class User(Base):\n'
        '\t"""User Base."""\n\n'
        '\t__tablename__ = "User"\n\n'
        '\t# Primary Keys\n'
        '\tid: Mapped[int] = mapped_column(Integer, primary_key=True)\n\n'
        '\t# Columns\n'
        '\tcompany_id: Mapped[UUID4] = mapped_column(UUID(as_uuid=True), ForeignKey("Company.id"))\n'
        '\temail: Mapped[str | None] = mapped_column(String)\n'
        '\t# Relationships\n'
        '\tcompany: Mapped[Company | None] = relationship("Company", back_populates="users", uselist=False)\n'
        '\t# Table Args\n'
        '\t__table_args__ = (\n'
        "\t\tPrimaryKeyConstraint('id', name='User_pkey'),\n"
        "\t\t{ 'schema': 'public' }\n"
        '\t)\n\n\n'
        'class Company(Base):\n'
        '\t"""Company Base."""\n\n'
        '\t__tablename__ = "Company"\n\n'
        '\t# Primary Keys\n'
        '\tid: Mapped[UUID4] = mapped_column(UUID(as_uuid=True), primary_key=True)\n\n'
        '\t# Columns\n'
        '\tname: Mapped[str] = mapped_column(String)\n'
        '\t# Table Args\n'
        '\t__table_args__ = (\n'
        "\t\tPrimaryKeyConstraint('id', name='Company_pkey'),\n"
        "\t\t{ 'schema': 'public' }\n"
        '\t)\n\n\n'
        'class Client(Base):\n'
        '\t"""Client Base."""\n\n'
        '\t__tablename__ = "Client"\n\n'
        '\t# Primary Keys\n'
        '\tid: Mapped[UUID4] = mapped_column(UUID(as_uuid=True), primary_key=True)\n\n'
        '\t# Columns\n'
        '\tname: Mapped[str] = mapped_column(String)\n'
        '\tinfo_json: Mapped[dict | Json | None] = mapped_column(JSONB)\n'
        '\t# Table Args\n'
        '\t__table_args__ = (\n'
        "\t\tPrimaryKeyConstraint('id', name='Client_pkey'),\n"
        "\t\t{ 'schema': 'public' }\n"
        '\t)'
    )
    assert fastapi_writer.write() == expected_value
