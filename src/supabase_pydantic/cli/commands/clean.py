import logging
from typing import Any

import click

from supabase_pydantic.cli.common import common_options, load_config
from supabase_pydantic.utils.io import clean_directories, get_working_directories

# Define framework choices - can be imported from a constants file later
framework_choices = ['fastapi']


@click.command()
@common_options
@click.pass_context
@click.option(
    '-d',
    '--dir',
    '--directory',
    'directory',
    default=None,  # Will use the config value if None
    required=False,
    help='The directory to clear of generated files and directories. Defaults to config value or "entities".',
)
def clean(ctx: Any, directory: str | None, config: str | None) -> None:
    """Clean the project directory by removing generated files and clearing caches."""
    # Load config if provided
    config_dict = {}
    if config:
        config_dict = load_config()

    click.echo('Cleaning up the project...')
    cfg_default_dir = config_dict.get('default_directory', 'entities')
    actual_directory = directory if directory is not None else cfg_default_dir
    logging.info(f'Cleaning directory: {actual_directory}')
    try:
        directories = get_working_directories(actual_directory, tuple(framework_choices), auto_create=False)
        clean_directories(directories)
    except (FileExistsError, FileNotFoundError):
        click.echo(f'Directory doesn\'t exist: "{actual_directory}". Exiting...')
        return
    except Exception as e:
        click.echo(f'An error occurred while cleaning the project: {e}')
        return
    else:
        click.echo('Project cleaned.')
