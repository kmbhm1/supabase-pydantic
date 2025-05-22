import logging
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
    RuffNotFoundError,
    ToolConfig,
    WriterConfig,
    clean_directories,
    construct_tables,
    format_with_ruff,
    generate_seed_data,
    get_standard_jobs,
    get_working_directories,
    local_default_env_configuration,
    write_seed_file,
)

# Pretty print for testing
pp = pprint.PrettyPrinter(indent=4)

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Standard choices
model_choices = ['pydantic']
framework_choices = ['fastapi']


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


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: Any) -> None:
    """A CLI tool for generating Pydantic models from a Supabase/PostgreSQL database.

    In the future, more ORM frameworks and databases will be supported. In the works:
    Django, REST Flask, SQLAlchemy, Tortoise-ORM, and more.

    Additionally, more REST API generators will be supported ...

    Stay tuned!
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    # When invoked without a subcommand, just show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return


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
def clean(ctx: Any, directory: str | None) -> None:
    """Clean the project directory by removing generated files and clearing caches."""
    click.echo('Cleaning up the project...')
    cfg_default_dir = ctx.obj.get('default_directory', 'entities')
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


# TODO: add this initialization command
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


@cli.command(short_help='Generates code with specified configurations.')  # noqa
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
@generator_config.option('--all-schemas', is_flag=True, help='Process all schemas in the database.')
@generator_config.option(
    '--schema',
    multiple=True,
    default=['public'],
    help='Specify one or more schemas to include. Defaults to public.',
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
@click.option(
    '--no-crud-models',
    is_flag=True,
    show_default=True,
    default=False,
    help='Do not generate Insert and Update model variants. Only generate the base Row models.',  # noqa: E501
)
@click.option(
    '--no-enums',
    is_flag=True,
    default=False,
    help='Do not generate Enum classes for enum columns (default: enums are generated).',
)
@click.option(
    '--debug/--no-debug',
    is_flag=True,
    default=False,
    help='Enable debug logging.',
)
def gen(
    models: tuple[str],
    frameworks: tuple[str],
    default_directory: str,
    overwrite: bool,
    null_parent_classes: bool,
    create_seed_data: bool,
    all_schemas: bool,
    schema: tuple[str],
    local: bool = False,
    # linked: bool = False,
    db_url: str | None = None,
    # project_id: str | None = None,
    no_crud_models: bool = False,
    no_enums: bool = False,
    debug: bool = False,
) -> None:
    """Generate models from a PostgreSQL database."""
    # Configure logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    logging.debug(f'Debug mode is {"on" if debug else "off"}')

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

    # Get the database schema and table details
    # Determine schemas to process
    schemas = ('*',) if all_schemas else tuple(schema)  # Use '*' as an indicator to fetch all schemas
    table_dict = construct_tables(conn_type=conn_type, schemas=schemas, **env_vars)

    schemas_with_no_tables = [k for k, v in table_dict.items() if len(v) == 0]
    if len(schemas_with_no_tables) > 0:
        print(f'The following schemas have no tables and will be skipped: {", ".join(schemas_with_no_tables)}')
    table_dict = {k: v for k, v in table_dict.items() if len(v) > 0}
    if all_schemas:  # Reset schemas if all_schemas is True
        schemas = tuple(table_dict.keys())

    # Configure the writer jobs
    std_jobs = get_standard_jobs(models, frameworks, dirs, schemas)
    jobs: dict[str, dict[str, WriterConfig]] = {}
    for k, v in std_jobs.items():
        jobs[k] = {}
        for job, c in v.items():
            if c.enabled is False:
                continue
            jobs[k][job] = c

    # Generate the models; Run jobs
    paths = []
    factory = FileWriterFactory()
    for s, j in jobs.items():  # s = schema, j = jobs
        tables = table_dict[s]
        for job, c in j.items():  # c = config
            logging.info(f'Generating {job} models...')
            p, vf = factory.get_file_writer(
                tables,
                c.fpath(),
                c.file_type,
                c.framework_type,
                add_null_parent_classes=null_parent_classes,
                generate_crud_models=not no_crud_models,
                generate_enums=not no_enums,
            ).save(overwrite)
            paths += [p, vf] if vf is not None else [p]
            logging.info(f"{job} models generated successfully for schema '{s}': {p}")

    # Format the generated files
    # Format the generated files
    for p in paths:
        try:
            format_with_ruff(p)
            logging.info(f'File formatted successfully: {p}')
        except RuffNotFoundError as e:
            logging.warning(str(e))  # The exception message is already descriptive
        except Exception as e:  # Catch any other unexpected errors during formatting
            logging.error(f'An unexpected error occurred while formatting {p}: {str(e)}')

    # Generate seed data
    if create_seed_data:
        logging.info('Generating seed data...')
        for s, j in jobs.items():  # s = schema, j = jobs
            # Generate seed data
            tables = table_dict[s]
            seed_data = generate_seed_data(tables)

            # Check if seed data was generated
            if len(seed_data) == 0:
                logging.warning(f'Failed to generate seed data for schema: {s}')
                if all([t.table_type == 'VIEW' for t in tables]):
                    logging.info('All entities are views in this schema. Skipping seed data generation...')
                else:
                    logging.error('Unknown error occurred; check the schema. Skipping seed data generation...')
                continue

            # Write the seed data
            d = dirs.get('default')
            fname = os.path.join(d if d is not None else 'entities', f'seed_{s}.sql')
            fpaths = write_seed_file(seed_data, fname, overwrite)
            print(f'Seed data generated successfully: {", ".join(fpaths)}')


if __name__ == '__main__':
    cli()  # keep; for testing & debugging  # noqa
