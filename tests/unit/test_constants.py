import re

from supabase_pydantic.util.constants import POSTGRES_SQL_CONN_REGEX, FrameWorkType, OrmType, WriterConfig


def test_WriterConfig_methods():
    """Test WriterConfig methods."""
    writer_config = WriterConfig(
        file_type=OrmType.PYDANTIC,
        framework_type=FrameWorkType.FASTAPI,
        filename='test.py',
        directory='foo',
        enabled=True,
    )
    assert writer_config.ext() == 'py'
    assert writer_config.name() == 'test'
    assert writer_config.fpath() == 'foo/test.py'
    assert writer_config.to_dict() == {
        'file_type': 'OrmType.PYDANTIC',
        'framework_type': 'FrameWorkType.FASTAPI',
        'filename': 'test.py',
        'directory': 'foo',
        'enabled': 'True',
    }


def test_postgres_db_string_regex():
    """Test the regex for a postgres database string."""
    pattern = re.compile(POSTGRES_SQL_CONN_REGEX)

    assert pattern.match('postgresql://localhost')
    assert pattern.match('postgresql://localhost:5433')
    assert pattern.match('postgresql://localhost/mydb')
    assert pattern.match('postgresql://user@localhost')
    assert pattern.match('postgresql://user:secret@localhost')
    assert pattern.match('postgresql://other@localhost/otherdb?connect_timeout=10&application_name=myapp')
    assert not pattern.match('postgresql://host1:123,host2:456/somedb?application_name=myapp')
    assert pattern.match('postgres://myuser:mypassword@192.168.0.100:5432/mydatabase')
    assert pattern.match('postgresql://192.168.0.100/mydb')

    assert not pattern.match('postgresql://')
    assert not pattern.match('postgresql://localhost:')
    assert pattern.match('postgresql://localhost:5433/')
    assert pattern.match('postgresql://localhost:5433/mydb?')
    assert pattern.match('postgresql://localhost:5433/mydb?connect_timeout=10&application_name=myapp')
    assert pattern.match('postgresql://postgres:postgres@127.0.0.1:54333')
