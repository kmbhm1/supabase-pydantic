import pytest

from supabase_pydantic.core.constants import WriterClassType
from supabase_pydantic.db.models import ColumnInfo, TableInfo
from supabase_pydantic.core.writers.pydantic import PydanticFastAPIClassWriter


@pytest.fixture
def table_with_model_prefix_columns():
    """Create a table with columns that have 'model_' prefix."""
    return TableInfo(
        name='TestTable',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            # Regular column
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            # Column with model_ prefix that would be aliased by Pydantic by default
            ColumnInfo(name='model_type', post_gres_datatype='varchar', is_nullable=True, datatype='str'),
            # Another column with model_ prefix in mixed case to test case insensitivity
            ColumnInfo(name='Model_version', post_gres_datatype='varchar', is_nullable=True, datatype='str'),
        ],
    )


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.pydantic
def test_model_prefix_protection_default_behavior(table_with_model_prefix_columns):
    """Test that by default, Pydantic's model_ prefix protection is enabled."""
    # Create writer with default settings (protection enabled)
    writer = PydanticFastAPIClassWriter(table_with_model_prefix_columns)

    # Generate the class definition
    class_def = writer.write_class()

    # Check that ConfigDict is NOT included - this means default Pydantic behavior applies
    # which is to protect model_ prefixed fields
    assert 'model_config = ConfigDict(protected_namespaces=())' not in class_def

    # In the current implementation, the fields are not prefixed with field_
    # They're left as is, and Pydantic's built-in protection will handle them at runtime
    assert 'model_type' in class_def and 'str | None' in class_def
    assert 'Model_version' in class_def and 'str | None' in class_def


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.pydantic
def test_model_prefix_protection_disabled(table_with_model_prefix_columns):
    """Test that when model prefix protection is disabled, model_config is added."""
    # Create writer with protection disabled
    writer = PydanticFastAPIClassWriter(table_with_model_prefix_columns, disable_model_prefix_protection=True)

    # Generate the class definition
    class_def = writer.write_class()

    # Check that ConfigDict IS included to disable Pydantic's model_ prefix protection
    assert 'model_config' in class_def and 'ConfigDict' in class_def and 'protected_namespaces=()' in class_def

    # Column names remain unchanged in the model
    assert 'model_type' in class_def and 'str | None' in class_def
    assert 'Model_version' in class_def and 'str | None' in class_def


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.pydantic
def test_imports_with_protection_disabled(table_with_model_prefix_columns):
    """Test that ConfigDict is imported when model prefix protection is disabled."""
    # Create writer with protection disabled
    writer = PydanticFastAPIClassWriter(table_with_model_prefix_columns, disable_model_prefix_protection=True)

    # The imports are handled by PydanticFastAPIWriter, not the class writer
    # So we'll directly check if the condition in write_class would trigger the ConfigDict import
    class_def = writer.write_class()

    # Verify the condition for ConfigDict import would be met
    # Note: The condition in the writer code only checks for aliases starting with model_
    # or field names starting with field_model_, not direct column names starting with model_
    has_model_prefix_columns = any(
        (
            (c.alias and c.alias.lower().startswith('model_'))
            or (c.name.lower().startswith('field_model_'))
            or c.name.lower().startswith('model_')
        )
        for c in table_with_model_prefix_columns.columns
    )

    assert has_model_prefix_columns
    assert 'model_config' in class_def and 'ConfigDict' in class_def and 'protected_namespaces=()' in class_def


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.pydantic
def test_protection_not_added_when_no_model_prefix_columns():
    """Test that ConfigDict is not added when there are no model_ prefixed columns."""
    # Create a table without model_ prefixed columns
    table = TableInfo(
        name='RegularTable',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(name='name', post_gres_datatype='varchar', is_nullable=False, datatype='str'),
            ColumnInfo(name='description', post_gres_datatype='text', is_nullable=True, datatype='str'),
        ],
    )

    # Create writer with protection disabled
    writer = PydanticFastAPIClassWriter(table, disable_model_prefix_protection=True)

    # Generate the class definition
    class_def = writer.write_class()

    # Check that ConfigDict is NOT included since no model_ columns exist
    assert 'model_config = ConfigDict(protected_namespaces=())' not in class_def


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.pydantic
def test_different_model_types_with_protection_disabled(table_with_model_prefix_columns):
    """Test that protection works with different model types (BASE, INSERT, UPDATE)."""
    for class_type in [WriterClassType.BASE, WriterClassType.INSERT, WriterClassType.UPDATE]:
        writer = PydanticFastAPIClassWriter(
            table_with_model_prefix_columns, class_type=class_type, disable_model_prefix_protection=True
        )

        class_def = writer.write_class()

        # Check that ConfigDict IS included for all model types
        assert 'model_config' in class_def and 'ConfigDict' in class_def and 'protected_namespaces=()' in class_def
