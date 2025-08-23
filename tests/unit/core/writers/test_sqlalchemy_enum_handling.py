import pytest

from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.models import ColumnInfo, TableInfo
from supabase_pydantic.core.writers.sqlalchemy import SqlAlchemyFastAPIClassWriter, SqlAlchemyFastAPIWriter


@pytest.fixture
def enum_table():
    """Return a TableInfo instance with enum columns for testing."""
    return TableInfo(
        name='Product',
        schema='public',
        columns=[
            ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
            ColumnInfo(
                name='status',
                post_gres_datatype='USER-DEFINED',
                is_nullable=False,
                datatype='status',
                enum_info=EnumInfo(
                    name='product_status', values=['active', 'inactive', 'discontinued'], schema='public'
                ),
            ),
            ColumnInfo(
                name='category',
                post_gres_datatype='USER-DEFINED',
                is_nullable=True,
                datatype='category',
                enum_info=EnumInfo(
                    name='product_category', values=['electronics', 'clothing', 'food'], schema='public'
                ),
            ),
        ],
    )


@pytest.fixture
def enum_tables():
    """Return TableInfo instances with different schema enums for testing."""
    return [
        TableInfo(
            name='Product',
            schema='public',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
                ColumnInfo(
                    name='status',
                    post_gres_datatype='USER-DEFINED',
                    is_nullable=False,
                    datatype='status',
                    enum_info=EnumInfo(
                        name='product_status', values=['active', 'inactive', 'discontinued'], schema='public'
                    ),
                ),
            ],
        ),
        TableInfo(
            name='Employee',
            schema='hr',
            columns=[
                ColumnInfo(name='id', post_gres_datatype='integer', is_nullable=False, primary=True, datatype='int'),
                ColumnInfo(
                    name='department',
                    post_gres_datatype='USER-DEFINED',
                    is_nullable=False,
                    datatype='department',
                    enum_info=EnumInfo(name='department', values=['sales', 'engineering', 'support'], schema='hr'),
                ),
                ColumnInfo(
                    name='status',
                    post_gres_datatype='USER-DEFINED',
                    is_nullable=True,
                    datatype='status',
                    enum_info=EnumInfo(
                        name='employee_status', values=['active', 'on_leave', 'terminated'], schema='hr'
                    ),
                ),
            ],
        ),
    ]


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.sqlalchemy
def test_SqlAlchemyFastAPIClassWriter_write_column_with_enum(enum_table):
    """Verify that write_column correctly formats enum columns."""
    writer = SqlAlchemyFastAPIClassWriter(enum_table)

    status_col = next(col for col in enum_table.columns if col.name == 'status')
    category_col = next(col for col in enum_table.columns if col.name == 'category')

    # Test non-nullable enum
    status_result = writer.write_column(status_col)
    assert 'Enum(*PublicProductStatusEnum._member_names_, name="product_status", schema="public")' in status_result
    assert 'Mapped[str]' in status_result

    # Test nullable enum
    category_result = writer.write_column(category_col)
    assert (
        'Enum(*PublicProductCategoryEnum._member_names_, name="product_category", schema="public")' in category_result
    )
    assert 'Mapped[str | None]' in category_result
    assert 'nullable=True' in category_result


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.sqlalchemy
def test_SqlAlchemyFastAPIWriter_collect_enum_infos(enum_tables):
    """Verify that _collect_enum_infos correctly collects all enum infos from tables."""
    writer = SqlAlchemyFastAPIWriter(enum_tables, 'dummy_path.py')

    enum_infos = writer._collect_enum_infos()

    # Should collect 3 enum infos across both schemas
    assert len(enum_infos) == 3

    # Check that all enum infos are collected
    enum_names = {f'{enum.schema}.{enum.name}' for enum in enum_infos}
    expected_names = {'public.product_status', 'hr.department', 'hr.employee_status'}
    assert enum_names == expected_names


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.sqlalchemy
def test_SqlAlchemyFastAPIWriter_generate_enum_classes(enum_tables):
    """Verify that _generate_enum_classes generates correct enum classes."""
    writer = SqlAlchemyFastAPIWriter(enum_tables, 'dummy_path.py')

    enum_classes = writer._generate_enum_classes()

    # Should generate 3 enum classes
    assert len(enum_classes) == 3

    # Check for public schema enum class
    public_enum = next((cls for cls in enum_classes if 'PublicProductStatusEnum' in cls), None)
    assert public_enum is not None
    assert 'class PublicProductStatusEnum(PyEnum):' in public_enum
    assert "\tACTIVE = 'active'" in public_enum
    assert "\tINACTIVE = 'inactive'" in public_enum
    assert "\tDISCONTINUED = 'discontinued'" in public_enum

    # Check for hr schema enum classes
    hr_dept_enum = next((cls for cls in enum_classes if 'HrDepartmentEnum' in cls), None)
    assert hr_dept_enum is not None
    assert 'class HrDepartmentEnum(PyEnum):' in hr_dept_enum
    assert "\tSALES = 'sales'" in hr_dept_enum
    assert "\tENGINEERING = 'engineering'" in hr_dept_enum
    assert "\tSUPPORT = 'support'" in hr_dept_enum

    hr_status_enum = next((cls for cls in enum_classes if 'HrEmployeeStatusEnum' in cls), None)
    assert hr_status_enum is not None
    assert 'class HrEmployeeStatusEnum(PyEnum):' in hr_status_enum
    assert "\tACTIVE = 'active'" in hr_status_enum
    assert "\tON_LEAVE = 'on_leave'" in hr_status_enum
    assert "\tTERMINATED = 'terminated'" in hr_status_enum


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.sqlalchemy
def test_SqlAlchemyFastAPIWriter_write_with_enums(enum_tables):
    """Verify that the full write output includes proper enum definitions."""
    writer = SqlAlchemyFastAPIWriter(enum_tables, 'dummy_path.py')

    output = writer.write()

    # Check imports
    assert 'from sqlalchemy import Enum' in output
    assert 'from enum import Enum as PyEnum' in output

    # Check enum class definitions
    assert 'class PublicProductStatusEnum(PyEnum):' in output
    assert 'class HrDepartmentEnum(PyEnum):' in output
    assert 'class HrEmployeeStatusEnum(PyEnum):' in output

    # Check enum field usage
    assert (
        'status: Mapped[str] = mapped_column(Enum(*PublicProductStatusEnum._member_names_, name="product_status", schema="public"))'
        in output
    )
    assert (
        'department: Mapped[str] = mapped_column(Enum(*HrDepartmentEnum._member_names_, name="department", schema="hr"))'
        in output
    )
