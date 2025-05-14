from typing import Any

import click

from src.supabase_pydantic.cli.common import config_dict, framework_choices

# Import get_working_directories here but import clean_directories later
# This helps with patching in tests
from src.supabase_pydantic.utils.io import get_working_directories


@click.command('clean', short_help='Cleans generated files.')
@click.pass_context
@click.option(
    '-d',  # short option
    '--dir',  # short option
    '--directory',
    'directory',
    default=config_dict.get('default_directory', 'entities'),
    required=False,
    help='The directory to clear of generated files and directories. Defaults to "entities".',
)
def clean(ctx: Any, directory: str) -> None:
    """Clean the project directory by removing generated files and clearing caches."""
    click.echo('Cleaning up the project...')
    try:
        directories = get_working_directories(directory, tuple(framework_choices), auto_create=False)

        # Import clean_directories here to make patching work in tests
        from src.supabase_pydantic.utils.io import clean_directories

        clean_directories(directories)
    except (FileExistsError, FileNotFoundError):
        click.echo(f'Directory doesn\'t exist: "{directory}". Exiting...')
        return
    except Exception as e:
        click.echo('An error occurred while cleaning the project')
        click.echo(f'Error details: {e}')
        return
    else:
        click.echo('Project cleaned.')
