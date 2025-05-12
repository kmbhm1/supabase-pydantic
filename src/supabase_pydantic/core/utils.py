"""Core utilities for the supabase-pydantic package."""

import logging
import os

# Re-export utility functions from the original codebase
# These will eventually be refactored into the core module
from src.supabase_pydantic.utils import (
    chunk_text,
    clean_directories,
    clean_directory,
    create_directories_if_not_exist,
    format_with_ruff,
    generate_seed_data,
    get_enum_member_from_string,
    get_pydantic_type,
    get_sqlalchemy_type,
    get_standard_jobs,
    get_working_directories,
    local_default_env_configuration,
    to_pascal_case,
    write_seed_file,
)


def check_readiness(env_vars: dict[str, str | None]) -> bool:
    """Check if environment variables are set correctly."""
    if not env_vars:
        logging.error('No environment variables provided.')
        return False
    for k, v in env_vars.items():
        logging.debug(f'Checking environment variable: {k}')
        if v is None:
            logging.error(f'Environment variables not set correctly. {k} is missing. Please set it in .env file.')
            return False

    logging.debug('All required environment variables are set')
    return True


def create_directory_if_not_exists(directory: str) -> None:
    """Create a directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f'Created directory: {directory}')


__all__ = [
    'check_readiness',
    'chunk_text',
    'clean_directories',
    'clean_directory',
    'create_directories_if_not_exist',
    'create_directory_if_not_exists',
    'format_with_ruff',
    'generate_seed_data',
    'get_enum_member_from_string',
    'get_pydantic_type',
    'get_sqlalchemy_type',
    'get_standard_jobs',
    'get_working_directories',
    'local_default_env_configuration',
    'to_pascal_case',
    'write_seed_file',
]
