"""Tests for WriterConfig in supabase_pydantic.core.config."""

from supabase_pydantic.core.config import WriterConfig
from supabase_pydantic.core.constants import FrameWorkType, OrmType


import pytest


@pytest.mark.unit
@pytest.mark.config
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
