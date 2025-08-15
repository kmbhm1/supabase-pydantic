import pytest

from supabase_pydantic.db.models import TableInfo
from supabase_pydantic.core.constants import FrameWorkType, OrmType
from supabase_pydantic.core.writers.factories import FileWriterFactory
from supabase_pydantic.core.writers.pydantic import PydanticFastAPIWriter
from supabase_pydantic.core.writers.sqlalchemy import SqlAlchemyFastAPIWriter


@pytest.fixture
def table_info():
    return [TableInfo(name='test_table', columns=[])]


@pytest.fixture
def file_path():
    return 'test_path.py'


@pytest.mark.parametrize(
    'file_type,framework_type,expected_writer',
    [
        (OrmType.SQLALCHEMY, FrameWorkType.FASTAPI, SqlAlchemyFastAPIWriter),
        (OrmType.PYDANTIC, FrameWorkType.FASTAPI, PydanticFastAPIWriter),
    ],
)
def test_get_file_writer_valid_cases(table_info, file_path, file_type, framework_type, expected_writer):
    writer = FileWriterFactory.get_file_writer(table_info, file_path, file_type, framework_type)
    assert isinstance(writer, expected_writer), f'Expected {expected_writer}, got {type(writer)}'


def test_get_file_writer_invalid_cases(table_info, file_path):
    with pytest.raises(ValueError) as excinfo:
        FileWriterFactory.get_file_writer(table_info, file_path, OrmType.PYDANTIC, FrameWorkType)
    assert 'Unsupported file type or framework type' in str(excinfo.value)
