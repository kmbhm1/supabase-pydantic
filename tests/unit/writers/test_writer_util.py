import datetime
import re
from unittest.mock import patch

import pytest

from supabase_pydantic.util.constants import WriterClassType
from supabase_pydantic.util.writers.util import (
    generate_unique_filename,
    get_base_class_post_script,
    get_section_comment,
)


@pytest.mark.parametrize(
    'table_type, class_type, expected_output',
    [
        ('VIEW', WriterClassType.PARENT, 'ViewBaseSchemaParent'),
        ('VIEW', WriterClassType.BASE, 'ViewBaseSchema'),
        ('TABLE', WriterClassType.PARENT, 'BaseSchemaParent'),
        ('TABLE', WriterClassType.BASE, 'BaseSchema'),
    ],
)
def test_get_base_class_post_script(table_type, class_type, expected_output):
    assert get_base_class_post_script(table_type, class_type) == expected_output


def test_generate_unique_filename():
    base_name = 'test'
    extension = '.py'
    directory = '/fake/directory'

    with patch('os.path.exists', side_effect=lambda x: x.endswith('test.py') or x.endswith('test_1.py')) as mock_exists:
        unique_filename = generate_unique_filename(base_name, extension, directory)
        match = re.search(r'test_(\d{20})\.py$', unique_filename)
        assert match is not None, f'Filename does not match the expected pattern: {unique_filename}'

        # Validate the datetime format
        # Assuming the format is YYYYMMDDHHMMSSffffffffff (year, month, day, hour, minute, second, microsecond)
        datetime_str = match.group(1)
        try:
            datetime.datetime.strptime(datetime_str, '%Y%m%d%H%M%S%f')
        except ValueError:
            assert False, 'Datetime format is incorrect'


def test_get_section_comment_without_notes():
    comment_title = 'Test Section'
    expected_output = '# TEST SECTION'
    assert get_section_comment(comment_title) == expected_output


def test_get_section_comment_with_notes():
    comment_title = 'Test Section'
    notes = ['This is a very long note that should be chunked into multiple lines to fit the width restriction.']
    expected_output = (
        '# TEST SECTION\n# Note: This is a '
        'very long note that should be chunked into multiple lines to\n'
        '# fit the width restriction.'
    )
    assert get_section_comment(comment_title, notes) == expected_output
