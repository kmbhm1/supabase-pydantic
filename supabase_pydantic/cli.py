import os
import pprint
import re
from typing import Any

import click
import toml
from click_option_group import OptionGroup, RequiredMutuallyExclusiveOptionGroup
from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.util import (
    POSTGRES_SQL_CONN_REGEX,
    AppConfig,
    DatabaseConnectionType,
    FileWriterFactory,
    ToolConfig,
    clean_directories,
    construct_tables,
    format_with_ruff,
    generate_seed_data,
    get_standard_jobs,
    get_working_directories,
    local_default_env_configuration,
    run_isort,
)
from supabase_pydantic.util.writers.util import write_seed_file

# Pretty print for testing
pp = pprint.PrettyPrinter(indent=4)

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Standard choices
# model_choices = ['pydantic', 'sqlalchemy']
# framework_choices = ['fastapi', 'fastapi-jsonapi']
model_choices = ['pydantic']
framework_choices = ['fastapi']


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
    show_default=True,
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
    show_default=True,
    type=click.Choice(framework_choices, case_sensitive=False),
    required=False,
    help='The framework to generate code for. This can be a space separated list of valid frameworks. Default is "fastapi".',  # noqa: E501
)
@generator_config.option(
    '--seed',
    'create_seed_data',
    is_flag=True,
    show_default=True,
    default=False,
    help='Generate seed data for the tables if possible.',
)
@connect_sources.option(
    '--local',
    is_flag=True,
    help='Use local database connection.',
)
@connect_sources.option(
    '--db-url',
    type=str,
    help='Use database URL for connection.',
)
@click.option(
    '-d',
    '--dir',
    'default_directory',
    multiple=False,
    default='entities',
    show_default=True,
    type=click.Path(exists=False, file_okay=False, dir_okay=True, resolve_path=True),
    help='The directory to save files',
    required=False,
)
@click.option(
    '--no-overwrite',
    'overwrite',
    is_flag=True,
    show_default=True,
    default=True,
    help='Overwrite existing files.',
)
@click.option(
    '--null-parent-classes',
    is_flag=True,
    show_default=True,
    default=False,
    help='In addition to the generated base classes, generate null parent classes for those base classes. For Pydantic models only.',  # noqa: E501
)
def gen(
    models: tuple[str],
    frameworks: tuple[str],
    default_directory: str,
    overwrite: bool,
    null_parent_classes: bool,
    create_seed_data: bool,
    local: bool = False,
    # linked: bool = False,
    db_url: str | None = None,
    # project_id: str | None = None,
) -> None:
    """Generate models from a PostgreSQL database."""
    # pp.pprint(locals())
    # Load environment variables from .env file & check if they are set correctly
    if not local and db_url is None:
        print('Please provide a connection source. Exiting...')
        return

    conn_type: DatabaseConnectionType = DatabaseConnectionType.LOCAL
    env_vars: dict[str, str | None] = dict()
    if db_url is not None:
        print('Checking local database connection.' + db_url)
        if re.match(POSTGRES_SQL_CONN_REGEX, db_url) is None:
            print(f'Invalid database URL: "{db_url}". Exiting.')
            return
        conn_type = DatabaseConnectionType.DB_URL
        env_vars['DB_URL'] = db_url
    else:
        load_dotenv(find_dotenv())
        env_vars.update(
            **{
                'DB_NAME': os.environ.get('DB_NAME', None),
                'DB_USER': os.environ.get('DB_USER', None),
                'DB_PASS': os.environ.get('DB_PASS', None),
                'DB_HOST': os.environ.get('DB_HOST', None),
                'DB_PORT': os.environ.get('DB_PORT', None),
            }
        )
        if any([v is None for v in env_vars.values()]) and local:
            print(
                f'Critical environment variables not set: {", ".join([k for k, v in env_vars.items() if v is None])}.'
            )
            print('Using default local values...')
            env_vars = local_default_env_configuration()
        # Check if environment variables are set correctly
        assert check_readiness(env_vars)

    # Get the directories for the generated files
    dirs = get_working_directories(default_directory, frameworks, auto_create=True)

    # Get the database schema details
    tables = construct_tables(conn_type, **env_vars)

    # Configure the writer jobs
    jobs = {k: v for k, v in get_standard_jobs(models, frameworks, dirs).items() if v.enabled}

    # Generate the models; Run jobs
    paths = []
    factory = FileWriterFactory()
    for job, c in jobs.items():  # c = config
        print(f'Generating {job} models...')
        p, vf = factory.get_file_writer(
            tables, c.fpath(), c.file_type, c.framework_type, add_null_parent_classes=null_parent_classes
        ).save(overwrite)
        paths += [p, vf] if vf is not None else [p]
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

    # Generate seed data
    if create_seed_data:
        print('Generating seed data...')
        try:
            seed_data = generate_seed_data(tables)
            d = dirs.get('default')
            fname = os.path.join(d if d is not None else 'entities', 'seed.sql')
            fpaths = write_seed_file(seed_data, fname, overwrite)
            print(f'Seed data generated successfully: {", ".join(fpaths)}')
        except Exception as e:
            print('Error creating seed data:', e)


if __name__ == '__main__':
    cli()
