from dataclasses import dataclass

from supabase_pydantic.util.dataclasses import ColumnInfo, TableInfo
from supabase_pydantic.util.writers.pydantic_writers import PydanticFastAPIClassWriter


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
    return ColumnInfo(
        name=name,
        post_gres_datatype=datatype,
        datatype=datatype,
        is_nullable=is_nullable,
        is_identity=False,
        enum_info=enum_info,
        primary=is_primary
    )


# Create a test table with enum array fields
table = TableInfo(
    name="test_table",
    columns=[
        create_test_column('id', 'bigint', is_nullable=False, is_primary=True),
        create_test_column('single_string_field', 'text', is_nullable=True),
        create_test_column("single_enum_field", "MyEnum", is_nullable=True,
                           enum_info=TestEnumInfo("myenum", ["ValueA", "ValueB", "ValueC"])),
        create_test_column('my_string_field', 'text[]', is_nullable=True),
        create_test_column("my_enum_field", "MyEnum[]", is_nullable=True,
                           enum_info=TestEnumInfo("myenum", ["ValueA", "ValueB", "ValueC"])),
        create_test_column('non_nullable_string_field', 'text[]', is_nullable=False),
        create_test_column("non_nullable_enum_field", "MyEnum[]", is_nullable=False,
                           enum_info=TestEnumInfo("myenum", ["ValueA", "ValueB", "ValueC"])),
    ],
    foreign_keys=[],
    constraints=[]
)

# Generate model
writer = PydanticFastAPIClassWriter(table, generate_enums=True)
model_code = writer.write_class()

print('Generated model code:')
print('=' * 80)
print(model_code)
print('=' * 80)
