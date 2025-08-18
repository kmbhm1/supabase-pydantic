"""Tests for I/O utilities in supabase_pydantic.utils.io."""

import os
import pytest
from unittest.mock import call, patch

from supabase_pydantic.utils.io import (
    clean_directories,
    clean_directory,
    create_directories_if_not_exist,
    get_working_directories,
)


@pytest.mark.unit
@pytest.mark.io
def test_clean_directory_empty():
    directory = 'mock_directory'
    with (
        patch('os.path.isdir', return_value=True),
        patch('os.listdir', return_value=[]),
        patch('shutil.rmtree') as mock_rmtree,
    ):
        clean_directory(directory)
        mock_rmtree.assert_called_once_with(directory)


@pytest.mark.unit
@pytest.mark.io
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


@pytest.mark.unit
@pytest.mark.io
def test_clean_directory_with_files_handles_error_silently():
    directory = 'mock_directory'
    files = ['file1.txt', 'dir1']
    with (
        patch('os.path.isdir', return_value=True),
        patch('os.listdir', return_value=files),
        patch('os.path.join', side_effect=lambda x, y: f'{x}/{y}'),
        patch('os.path.isfile', side_effect=lambda x: 'txt' in x),
        patch('os.path.isdir', side_effect=lambda x: 'dir' in x),
        patch('os.unlink', side_effect=Exception('foo')),
        patch('shutil.rmtree') as mock_rmtree,
        patch('supabase_pydantic.utils.io.logger.error') as mock_logger_error,
    ):
        clean_directory(directory)
        mock_rmtree.assert_called_with(directory)

        # Check if the correct logger statements were called
        expected_logger_calls = [
            call('An error occurred while deleting mock_directory/file1.txt.'),
            call('foo'),
        ]
        mock_logger_error.assert_has_calls(expected_logger_calls, any_order=True)


@pytest.mark.unit
@pytest.mark.io
def test_clean_directories():
    directories = {'default': 'default_directory', 'temp': 'temp_directory', 'backup': None, 'log': 'log_directory'}
    with (
        patch('os.path.isdir', return_value=True),
        patch('supabase_pydantic.utils.io.clean_directory') as mock_clean_dir,
    ):
        clean_directories(directories)

        # Assertions to check calls were made correctly
        expected_calls = [call('default_directory'), call('temp_directory'), call('log_directory')]
        mock_clean_dir.assert_has_calls(expected_calls, any_order=True)
        assert mock_clean_dir.call_count == 3


@pytest.mark.unit
@pytest.mark.io
def test_clean_directories_ignores_non_directories():
    directories = {'default': 'default_directory', 'temp': 'temp_directory', 'backup': None, 'log': 'log_directory'}
    with (
        patch('os.path.isdir', return_value=False),
        patch('supabase_pydantic.utils.io.logger.info') as mock_logger_info,
        patch('supabase_pydantic.utils.io.logger.warning') as mock_logger_warning,
        patch('supabase_pydantic.utils.io.clean_directory') as mock_clean_dir,
    ):
        clean_directories(directories)

        # Assertions to check calls were made correctly
        expected_calls = [call('default_directory')]
        mock_clean_dir.assert_has_calls(expected_calls, any_order=True)
        assert mock_clean_dir.call_count == 1

        # Check if the correct logger statements were called
        expected_info_calls = [
            call('Checking for directory: temp_directory'),
            call('Checking for directory: log_directory'),
            call('Removing default directory default_directory ...'),
            call('Default directory removed.'),
        ]
        expected_warning_calls = [
            call('Directory "temp_directory" does not exist. Skipping ...'),
            call('Directory "log_directory" does not exist. Skipping ...'),
        ]
        mock_logger_info.assert_has_calls(expected_info_calls, any_order=True)
        mock_logger_warning.assert_has_calls(expected_warning_calls, any_order=True)


@pytest.mark.unit
@pytest.mark.io
def test_get_working_directories_returns_correct_list():
    default_directory = 'default_directory'
    frameworks = ('fastapi',)
    for auto_create in [False, True]:
        with (
            patch('os.path.exists', return_value=False),
            patch('os.path.isdir', return_value=True),
            patch('supabase_pydantic.utils.io.logger.warning') as mock_logger_warning,
            patch('supabase_pydantic.utils.io.create_directories_if_not_exist') as mock_create_dirs,
        ):
            directories = get_working_directories(default_directory, frameworks, auto_create)

            assert directories == {
                'default': default_directory,
                'fastapi': os.path.join(default_directory, 'fastapi'),
            }

            # Check for warning message
            mock_logger_warning.assert_called_once_with(f'Directory {default_directory} does not exist.')

            if auto_create:
                mock_create_dirs.assert_called_once_with(directories)
            else:
                mock_create_dirs.assert_not_called()


@pytest.mark.unit
@pytest.mark.io
def test_create_directories_if_not_exist_handles_creating_directories_correctly():
    directories = {'default': 'default_directory', 'temp': 'temp_directory', 'backup': None, 'log': 'log_directory'}

    # Assumption: directories should be created if they do not exist or are not directories
    # and should not be created if None is provided as a value in the dictionary

    tests = [(True, True), (False, True), (True, False), (False, False)]  # Test all combinations
    for i, (isdir, exists) in enumerate(tests):
        with (
            patch('os.path.isdir', return_value=isdir),
            patch('os.path.exists', return_value=exists),
            patch('supabase_pydantic.utils.io.logger.info') as mock_logger_info,
            patch('os.makedirs') as mock_makedirs,
        ):
            create_directories_if_not_exist(directories)

            # Assertions to check calls were made correctly
            if all([isdir, exists]):
                mock_logger_info.assert_not_called()
                mock_makedirs.assert_not_called()
            else:
                expected_calls = [call('default_directory'), call('temp_directory'), call('log_directory')]
                info_calls = [
                    call('Creating directory: temp_directory'),
                    call('Creating directory: log_directory'),
                    call('Creating directory: default_directory'),
                ]
                mock_makedirs.assert_has_calls(expected_calls, any_order=True)
                assert mock_makedirs.call_count == len(expected_calls)
                mock_logger_info.assert_has_calls(info_calls, any_order=True)
                assert mock_logger_info.call_count == len(info_calls)
