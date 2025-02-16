import pytest

from supabase_pydantic.util.dataclasses import ColumnInfo, TableInfo
from supabase_pydantic.util.writers.pydantic_writers import PydanticFastAPIClassWriter


@pytest.fixture
def table_info():
    """Return a TableInfo instance with constrained columns for testing."""
    return TableInfo(
        name='User',
        schema='public',
        columns=[
            ColumnInfo(
                name='country_code',
                post_gres_datatype='text',
                is_nullable=False,
                datatype='str',
                constraint_definition='CHECK (length(country_code) = 2)',
            ),
            ColumnInfo(
                name='username',
                post_gres_datatype='text',
                is_nullable=False,
                datatype='str',
                constraint_definition='CHECK (length(username) >= 4 AND length(username) <= 20)',
            ),
            ColumnInfo(
                name='description',
                post_gres_datatype='text',
                is_nullable=True,
                datatype='str',
                constraint_definition='CHECK (length(description) <= 100)',
            ),
        ],
        foreign_keys=[],
        constraints=[],
    )


@pytest.fixture
def writer(table_info):
    """Return a PydanticFastAPIClassWriter instance for testing."""
    return PydanticFastAPIClassWriter(table_info)


def test_write_column_with_length_constraints(writer):
    """Test that write_column correctly handles length constraints for text fields."""
    # Test fixed length (country_code)
    country_code_col = writer.write_column(writer.table.columns[0])
    assert "country_code: Annotated[str, StringConstraints(**{'min_length': 2, 'max_length': 2})]" in country_code_col

    # Test min and max length (username)
    username_col = writer.write_column(writer.table.columns[1])
    assert "username: Annotated[str, StringConstraints(**{'min_length': 4, 'max_length': 20})]" in username_col

    # Test max length with nullable (description)
    description_col = writer.write_column(writer.table.columns[2])
    assert (
        "description: Annotated[str, StringConstraints(**{'max_length': 100})] | None = Field(default=None)"
        in description_col
    )

    # Test min and max length constraints
    table = TableInfo(
        name='User',
        schema='public',
        columns=[
            ColumnInfo(
                name='description',
                post_gres_datatype='text',
                is_nullable=True,
                datatype='str',
                constraint_definition='CHECK (length(description) >= 10 AND length(description) <= 100)',
            )
        ],
    )
    writer = PydanticFastAPIClassWriter(table)
    result = writer.write_column(table.columns[0])
    expected = "description: Annotated[str, StringConstraints(**{'min_length': 10, 'max_length': 100})] | None = Field(default=None)"
    assert result == expected

    # Test only max length constraint
    table.columns[0].constraint_definition = 'CHECK (length(description) <= 50)'
    result = writer.write_column(table.columns[0])
    expected = "description: Annotated[str, StringConstraints(**{'max_length': 50})] | None = Field(default=None)"
    assert result == expected

    # Test only min length constraint
    table.columns[0].constraint_definition = 'CHECK (length(description) >= 5)'
    result = writer.write_column(table.columns[0])
    expected = "description: Annotated[str, StringConstraints(**{'min_length': 5})] | None = Field(default=None)"
    assert result == expected

    # Test no length constraints
    table.columns[0].constraint_definition = None
    result = writer.write_column(table.columns[0])
    expected = 'description: str | None = Field(default=None)'
    assert result == expected
