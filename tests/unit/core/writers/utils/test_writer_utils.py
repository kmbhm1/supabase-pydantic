"""Tests for writer utilities in supabase_pydantic.core.writers.utils."""

from unittest.mock import call, mock_open, patch

import pytest

from supabase_pydantic.core.writers.utils import get_latest_filename, write_seed_file


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.io
def test_get_latest_filename():
    file_path = 'directory/test_file.py'
    latest_file = get_latest_filename(file_path)
    assert latest_file == 'directory/test_file_latest.py'


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.io
def test_write_seed_file_no_overwrite_file_does_not_exist():
    seed_data = {
        'table1': [['id', 'name'], [1, 'Alice'], [2, 'Bob']],
        'table2': [['id', 'value'], [1, 'Value1'], [2, 'Value2']],
    }
    file_path = 'path/to/seed.sql'
    expected = ['path/to/seed_latest.sql']

    m = mock_open()

    with patch('builtins.open', m):
        with patch('os.path.exists', return_value=False):
            with patch('pathlib.Path.write_text'):
                with patch('pathlib.Path.exists', return_value=False):
                    result = write_seed_file(seed_data, file_path, overwrite=False)

    assert result == expected
    expected_calls = [
        call('-- table1\n'),
        call('INSERT INTO table1 (id, name) VALUES (1, Alice);\n'),
        call('INSERT INTO table1 (id, name) VALUES (2, Bob);\n'),
        call('\n'),
        call('-- table2\n'),
        call('INSERT INTO table2 (id, value) VALUES (1, Value1);\n'),
        call('INSERT INTO table2 (id, value) VALUES (2, Value2);\n'),
        call('\n'),
    ]
    m().write.assert_has_calls(expected_calls, any_order=True)


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.io
def test_write_seed_file_no_overwrite_file_exists():
    seed_data = {
        'table1': [['id', 'name'], [1, 'Alice'], [2, 'Bob']],
        'table2': [['id', 'value'], [1, 'Value1'], [2, 'Value2']],
    }
    file_path = 'path/to/seed.sql'
    expected_file_path = 'path/to/seed_latest.sql'
    unique_file_path = 'path/to/seed_unique.sql'

    m = mock_open()

    with patch('builtins.open', m):
        with patch('os.path.exists', return_value=True):
            with patch('supabase_pydantic.core.writers.utils.generate_unique_filename', return_value=unique_file_path):
                result = write_seed_file(seed_data, file_path, overwrite=False)

    assert result == [expected_file_path, unique_file_path]
    expected_calls = [
        call('-- table1\n'),
        call('INSERT INTO table1 (id, name) VALUES (1, Alice);\n'),
        call('INSERT INTO table1 (id, name) VALUES (2, Bob);\n'),
        call('\n'),
        call('-- table2\n'),
        call('INSERT INTO table2 (id, value) VALUES (1, Value1);\n'),
        call('INSERT INTO table2 (id, value) VALUES (2, Value2);\n'),
        call('\n'),
    ]
    m().write.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.unit
@pytest.mark.writers
@pytest.mark.io
def test_write_seed_file_overwrite():
    seed_data = {
        'table1': [['id', 'name'], [1, 'Alice'], [2, 'Bob']],
        'table2': [['id', 'value'], [1, 'Value1'], [2, 'Value2']],
    }
    file_path = 'path/to/seed.sql'
    expected = 'path/to/seed_latest.sql'

    m = mock_open()

    with patch('builtins.open', m):
        with patch('os.path.exists', return_value=True):
            with patch('pathlib.Path.write_text'):
                with patch('pathlib.Path.exists', return_value=True):
                    result = write_seed_file(seed_data, file_path, overwrite=True)

    assert result == [expected]
    expected_calls = [
        call('-- table1\n'),
        call('INSERT INTO table1 (id, name) VALUES (1, Alice);\n'),
        call('INSERT INTO table1 (id, name) VALUES (2, Bob);\n'),
        call('\n'),
        call('-- table2\n'),
        call('INSERT INTO table2 (id, value) VALUES (1, Value1);\n'),
        call('INSERT INTO table2 (id, value) VALUES (2, Value2);\n'),
        call('\n'),
    ]
    m().write.assert_has_calls(expected_calls, any_order=True)
