import os
import pprint
from typing import Any

import click
import toml
from click_option_group import OptionGroup, RequiredMutuallyExclusiveOptionGroup
from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.util import (
    AppConfig,
    FileWriterFactory,
    ToolConfig,
    clean_directories,
    construct_table_info_from_postgres,
    format_with_ruff,
    get_standard_jobs,
    get_working_directories,
    local_default_env_configuration,
    run_isort,
)

# Pretty print for testing
pp = pprint.PrettyPrinter(indent=4)

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Standard choices
model_choices = ['pydantic', 'sqlalchemy']
framework_choices = ['fastapi', 'fastapi-jsonapi']


def check_readiness(env_vars: dict[str, str | None]) -> bool:
    """Check if environment variables are set correctly."""
    if not env_vars:
        print('No environment variables provided.')
        return False
    for k, v in env_vars.items():
        # print(k, v)
        if v is None:
            print(f'Environment variables not set correctly. {k} is missing. Please set it in .env file.')
            return False

    return True


def load_config() -> AppConfig:
    """Load the configuration from the pyproject.toml file."""
    try:
        with open('pyproject.toml') as f:
            config_data: dict[str, Any] = toml.load(f)
            tool_config: ToolConfig = config_data.get('tool', {})
            app_config: AppConfig = tool_config.get('supabase_pydantic', {})
            return app_config
    except FileNotFoundError:
        return {}


config_dict: AppConfig = load_config()


# click


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx: Any, debug: bool) -> None:
    """A CLI tool for generating Pydantic models from a Supabase/PostgreSQL database.

    In the future, more ORM frameworks and databases will be supported. In the works:
    Django, REST Flask, SQLAlchemy, Tortoise-ORM, and more.

    Additionally, more REST API generators will be supported ...

    Stay tuned!
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj['DEBUG'] = debug
    # use as: click.echo(f"Debug is {'on' if ctx.obj['DEBUG'] else 'off'}")


@cli.command('clean', short_help='Cleans generated files.')
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
        clean_directories(directories)
    except (FileExistsError, FileNotFoundError):
        click.echo(f'Directory doesn\'t exist: "{directory}". Exiting...')
        return
    except Exception as e:
        click.echo(f'An error occurred while cleaning the project: {e}')
        return
    else:
        click.echo('Project cleaned.')


# @cli.command('init', short_help='Initializes the project for supabase-pydantic.')
# def init_project() -> None:
#     """This command initializes the project for supabase-pydantic."""
#     click.echo('Initializing the project...')
#     pass

generator_config = OptionGroup('Generator Options', help='Options for generating code.')
connect_sources = RequiredMutuallyExclusiveOptionGroup('Connection Configuration', help='The sources of the input data')

# TODO: add these as options for connection sources
# @connect_sources.option(
#     '--linked',
#     is_flag=True,
#     help='Use linked database connection.',
# )
# @connect_sources.option(
#     '--dburl',
#     type=str,
#     help='Use database URL for connection.',
# )
# @connect_sources.option(
#     '--project-id',
#     type=str,
#     help='Use project ID for connection.',
# )


@cli.command(short_help='Generates code with specified configurations.')
@generator_config.option(
    '-t',
    '--type',
    'models',
    multiple=True,
    default=['pydantic'],
    type=click.Choice(model_choices, case_sensitive=False),
    required=False,
    help='The model type to generate. This can be a space separated list of valid model types. Default is "pydantic".',
)
@generator_config.option(
    '-r',
    '--framework',
    'frameworks',
    multiple=True,
    default=['fastapi'],
    type=click.Choice(framework_choices, case_sensitive=False),
    required=False,
    help='The framework to generate code for. This can be a space separated list of valid frameworks. Default is "fastapi".',  # noqa: E501
)
@connect_sources.option(
    '--local',
    is_flag=True,
    help='Use local database connection.',
)
@click.option(
    '-d',
    '--dir',
    'default_directory',
    multiple=False,
    default='entities',
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    help='The directory to save files. Defaults to "entities".',
    required=False,
)
@click.option('--overwrite/--no-overwrite', default=True, help='Overwrite existing files. Defaults to overwrite.')
def gen(
    models: tuple[str],
    frameworks: tuple[str],
    default_directory: str,
    overwrite: bool,
    local: bool = False,
    # linked: bool = False,
    # dburl: str | None = None,
    # project_id: str | None = None,
) -> None:
    """Generate models from a PostgreSQL database."""
    # pp.pprint(locals())
    # if dburl is None and project_id is None and not local and not linked:
    #     print('Please provide a connection source. Exiting...')
    #     return

    # Load environment variables from .env file & check if they are set correctly
    if not local:
        print('Only local connection is supported at the moment. Exiting...')
        return

    load_dotenv(find_dotenv())
    env_vars: dict[str, str | None] = {
        'DB_NAME': os.environ.get('DB_NAME', None),
        'DB_USER': os.environ.get('DB_USER', None),
        'DB_PASS': os.environ.get('DB_PASS', None),
        'DB_HOST': os.environ.get('DB_HOST', None),
        'DB_PORT': os.environ.get('DB_PORT', None),
    }
    if any([v is None for v in env_vars.values()]) and local:
        print(f'Critical environment variables not set: {", ".join([k for k, v in env_vars.items() if v is None])}.')
        print('Using default local values...')
        env_vars = local_default_env_configuration()

    # Check if environment variables are set correctly
    assert check_readiness(env_vars)

    # Get the directories for the generated files
    dirs = get_working_directories(default_directory, frameworks, auto_create=True)

    # Get the database schema details
    tables = construct_table_info_from_postgres(
        env_vars['DB_NAME'], env_vars['DB_USER'], env_vars['DB_PASS'], env_vars['DB_HOST'], env_vars['DB_PORT']
    )

    # Configure the writer jobs
    jobs = {k: v for k, v in get_standard_jobs(models, frameworks, dirs).items() if v.enabled}

    # Generate the models; Run jobs
    paths = []
    factory = FileWriterFactory()
    for job, c in jobs.items():  # c = config
        print(f'Generating {job} models...')
        p = factory.get_file_writer(tables, c.fpath(), c.file_type, c.framework_type).save(overwrite)
        paths.append(p)
        print(f'{job} models generated successfully: {p}')

    # Format the generated files
    try:
        for p in paths:
            run_isort(p)
            format_with_ruff(p)
            print(f'File formatted successfully: {p}')
    except Exception as e:
        print('An error occurred while running isort and ruff: ')
        print(e)


if __name__ == '__main__':
    cli()
