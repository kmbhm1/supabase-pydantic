"""Command to clean generated files."""

from typing import Any

import click

from src.supabase_pydantic.core.utils import clean_directories, get_working_directories


@click.command('clean', short_help='Cleans generated files.')
@click.pass_context
@click.option(
    '-d',  # short option
    '--dir',
    '--directory',
    'directory',
    required=False,
    help='The directory to clear of generated files and directories. Defaults to "entities".',
)
def clean(ctx: Any, directory: str = 'entities') -> None:
    """Clean the project directory by removing generated files and clearing caches."""
    from src.supabase_pydantic.cli.main import framework_choices

    click.echo('Cleaning up the project...')
    try:
        directories = get_working_directories(directory, tuple(framework_choices), auto_create=False)
        clean_directories(directories)
    except (FileExistsError, FileNotFoundError):
        click.echo(f'Directory doesn\'t exist: "{directory}". Exiting...')
        return
    except Exception as e:
        click.echo(f'An error occurred while cleaning the project: {e}')
        return
    else:
        click.echo('Project cleaned successfully.')
