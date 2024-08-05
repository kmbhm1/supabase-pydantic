import pytest
from unittest.mock import patch
from supabase_pydantic.util.constants import WriterClassType
from supabase_pydantic.util.writers.util import (
    get_base_class_post_script,
    generate_unique_filename,
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
        assert unique_filename == '/fake/directory/test_2.py'


def test_get_section_comment_without_notes():
    comment_title = 'Test Section'
    expected_output = '############################## Test Section'
    assert get_section_comment(comment_title) == expected_output


def test_get_section_comment_with_notes():
    comment_title = 'Test Section'
    notes = ['This is a very long note that should be chunked into multiple lines to fit the width restriction.']
    expected_output = (
        '############################## Test Section\n# Note: This is a '
        'very long note that should be chunked into multiple lines to\n'
        '# fit the width restriction.'
    )
    assert get_section_comment(comment_title, notes) == expected_output
