import os
import pytest

from unittest.mock import call, patch

from supabase_pydantic.util.constants import FrameWorkType, OrmType, WriterConfig
from supabase_pydantic.util.util import (
    chunk_text,
    clean_directories,
    clean_directory,
    create_directories_if_not_exist,
    get_pydantic_type,
    get_sqlalchemy_type,
    get_enum_member_from_string,
    get_standard_jobs,
    get_working_directories,
    to_pascal_case,
)


def test_to_pascal_case():
    """Test to_pascal_case."""
    assert to_pascal_case('snake_case') == 'SnakeCase'
    assert to_pascal_case('snake_case_with_more_words') == 'SnakeCaseWithMoreWords'
    assert to_pascal_case('snake') == 'Snake'
    assert to_pascal_case('snake_case_with_1_number') == 'SnakeCaseWith1Number'
    assert to_pascal_case('snake_case_with_1_number_and_1_symbol!') == 'SnakeCaseWith1NumberAnd1Symbol!'


def test_chunk_text():
    """Test chunk_text."""
    text = 'This is a test text that will be split into lines with a maximum number of characters.'
    lines = chunk_text(text, nchars=40)
    assert lines == [
        'This is a test text that will be split',
        'into lines with a maximum number of',
        'characters.',
    ]


def test_clean_directory_empty():
    directory = 'mock_directory'
    with (
        patch('os.path.isdir', return_value=True),
        patch('os.listdir', return_value=[]),
        patch('shutil.rmtree') as mock_rmtree,
    ):
        clean_directory(directory)
        mock_rmtree.assert_called_once_with(directory)


def test_clean_directory_with_files():
    directory = 'mock_directory'
    files = ['file1.txt', 'dir1']
    with (
        patch('os.path.isdir', return_value=True),
        patch('os.listdir', return_value=files),
        patch('os.path.join', side_effect=lambda x, y: f'{x}/{y}'),
        patch('os.path.isfile', side_effect=lambda x: 'txt' in x),
        patch('os.path.isdir', side_effect=lambda x: 'dir' in x),
        patch('os.unlink') as mock_unlink,
        patch('shutil.rmtree') as mock_rmtree,
    ):
        clean_directory(directory)
        mock_unlink.assert_called_once_with(f'{directory}/file1.txt')
        mock_rmtree.assert_called_with(directory)


def test_clean_directory_with_files_handles_error_silently():
    directory = 'mock_directory'
    files = ['file1.txt', 'dir1']
    with (
        patch('os.path.isdir', return_value=True),
        patch('os.listdir', return_value=files),
        patch('os.path.join', side_effect=lambda x, y: f'{x}/{y}'),
        patch('os.path.isfile', side_effect=Exception('foo')),
        patch('os.path.isdir', side_effect=lambda x: 'dir' in x),
        patch('os.unlink') as mock_unlink,
        patch('shutil.rmtree') as mock_rmtree,
        patch('builtins.print') as mock_print,
    ):
        clean_directory(directory)
        mock_unlink.assert_not_called()
        mock_rmtree.assert_called_with(directory)

        # Check if the correct print statements were called
        expected_print_calls = [
            call('An error occurred while deleting mock_directory/file1.txt.'),
            call('foo'),
        ]
        mock_print.assert_has_calls(expected_print_calls, any_order=True)


def test_clean_directories():
    directories = {'default': 'default_directory', 'temp': 'temp_directory', 'backup': None, 'log': 'log_directory'}
    with (
        patch('os.path.isdir', return_value=True),
        patch('supabase_pydantic.util.util.clean_directory') as mock_clean_dir,
    ):  # Adjust the path to match your module structure
        clean_directories(directories)

        # Assertions to check calls were made correctly
        expected_calls = [call('default_directory'), call('temp_directory'), call('log_directory')]
        mock_clean_dir.assert_has_calls(expected_calls, any_order=True)
        assert mock_clean_dir.call_count == 3


def test_clean_directories_ignores_non_directories():
    directories = {'default': 'default_directory', 'temp': 'temp_directory', 'backup': None, 'log': 'log_directory'}
    with (
        patch('os.path.isdir', return_value=False),
        patch('builtins.print') as mock_print,
        patch('supabase_pydantic.util.util.clean_directory') as mock_clean_dir,
    ):  # Adjust the path to match your module structure
        clean_directories(directories)

        # Assertions to check calls were made correctly
        expected_calls = [call('default_directory')]
        mock_clean_dir.assert_has_calls(expected_calls, any_order=True)
        assert mock_clean_dir.call_count == 1

        # Check if the correct print statements were called
        expected_print_calls = [
            call('Directory temp_directory does not exist. Skipping ...'),
            call('Directory log_directory does not exist. Skipping ...'),
        ]
        mock_print.assert_has_calls(expected_print_calls, any_order=True)


def test_get_working_directories_returns_correct_list():
    default_directory = 'default_directory'
    frameworks = ('fastapi', 'fastapi-jsonapi')
    for auto_create in [False, True]:
        with (
            patch('os.path.exists', return_value=False),
            patch('os.path.isdir', return_value=True),
            patch('supabase_pydantic.util.util.create_directories_if_not_exist') as mock_create_dirs,
        ):
            directories = get_working_directories(default_directory, frameworks, auto_create)

            assert directories == {
                'default': default_directory,
                'fastapi': os.path.join(default_directory, 'fastapi'),
                'fastapi-jsonapi': os.path.join(default_directory, 'fastapi_jsonapi'),
            }

            if auto_create:
                mock_create_dirs.assert_called_once_with(directories)
            else:
                mock_create_dirs.assert_not_called()


def test_create_directories_if_not_exist_handles_creating_directories_correctly():
    directories = {'default': 'default_directory', 'temp': 'temp_directory', 'backup': None, 'log': 'log_directory'}

    # Assumption: directories should be created if they do not exist or are not directories
    # and should not be created if None is provided as a value in the dictionary

    tests = [(True, True), (False, True), (True, False), (False, False)]  # Test all combinations
    for i, (isdir, exists) in enumerate(tests):
        print(f'Test {i}: isdir={isdir}, exists={exists}')
        with (
            patch('os.path.isdir', return_value=isdir),
            patch('os.path.exists', return_value=exists),
            patch('builtins.print') as mock_print,
            patch('os.makedirs') as mock_makedirs,
        ):
            create_directories_if_not_exist(directories)

            # Assertions to check calls were made correctly
            if all([isdir, exists]):
                mock_makedirs.assert_not_called()
                mock_print.assert_not_called()
            else:
                expected_calls = [call('default_directory'), call('temp_directory'), call('log_directory')]
                print_calls = [
                    call('Creating directory: temp_directory'),
                    call('Creating directory: log_directory'),
                    call('Creating directory: default_directory'),
                ]
                mock_makedirs.assert_has_calls(expected_calls, any_order=True)
                assert mock_makedirs.call_count == len(expected_calls)
                mock_print.assert_has_calls(print_calls, any_order=True)
                assert mock_print.call_count == len(print_calls)


def test_all_postgres_data_types_are_mapped_to_pydantic_and_sqlalchemy():
    """Test that all PostgreSQL data types are mapped to Pydantic and SQLAlchemy types."""
    postgres_data_types = [
        'smallint',
        'integer',
        'bigint',
        'decimal',
        'numeric',
        'real',
        'double precision',
        'serial',
        'bigserial',
        'money',
        'character varying(n)',
        'varchar(n)',
        'character(n)',
        'char(n)',
        'text',
        'bytea',
        'timestamp',
        'timestamp with time zone',
        'date',
        'time',
        'time with time zone',
        'interval',
        'boolean',
        'enum',
        'point',
        'line',
        'lseg',
        'box',
        'path',
        'polygon',
        'circle',
        'cidr',
        'inet',
        'macaddr',
        'macaddr8',
        'bit',
        'bit varying',
        'tsvector',
        'tsquery',
        'uuid',
        'xml',
        'json',
        'jsonb',
        'integer[]',
        'any',
        'void',
        'record',
    ]

    for data_type in postgres_data_types:
        assert get_pydantic_type(data_type) is not None
        assert get_sqlalchemy_type(data_type) is not None


def test_get_enum_member_from_string_and_enums():
    """Test get_enum_member_from_string and FrameWorkType & OrmType."""
    assert get_enum_member_from_string(OrmType, 'pydantic') == OrmType.PYDANTIC
    assert get_enum_member_from_string(OrmType, 'sqlalchemy') == OrmType.SQLALCHEMY
    with pytest.raises(ValueError):
        get_enum_member_from_string(OrmType, 'invalid')

    assert get_enum_member_from_string(FrameWorkType, 'fastapi') == FrameWorkType.FASTAPI
    assert get_enum_member_from_string(FrameWorkType, 'fastapi-jsonapi') == FrameWorkType.FASTAPI_JSONAPI
    with pytest.raises(ValueError):
        get_enum_member_from_string(FrameWorkType, 'invalid')


def test_get_standard_jobs_returns_jobs():
    models = ('pydantic', 'sqlalchemy')
    frameworks = ('fastapi', 'fastapi-jsonapi')
    dirs = {
        'fastapi': 'fastapi_directory',
        'fastapi-jsonapi': 'fastapi_jsonapi_directory',
    }

    jobs = get_standard_jobs(models, frameworks, dirs)

    assert all([isinstance(job, WriterConfig) for job in jobs.values()])
