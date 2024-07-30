from supabase_pydantic.util.constants import FrameWorkType, OrmType, WriterConfig


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
