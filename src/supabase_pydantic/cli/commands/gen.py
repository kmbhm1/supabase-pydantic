"""Command for generating models from database schema."""

import logging
import os
import re

import click
from click_option_group import OptionGroup, RequiredMutuallyExclusiveOptionGroup
from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.cli.common import (
    check_readiness,
    framework_choices,
    model_choices,
)
from supabase_pydantic.core.config import WriterConfig, get_standard_jobs, local_default_env_configuration
from supabase_pydantic.core.writers.factories import FileWriterFactory
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.marshalers.schema import construct_tables
from supabase_pydantic.db.seed import generate_seed_data, write_seed_file
from supabase_pydantic.utils.constants import POSTGRES_SQL_CONN_REGEX
from supabase_pydantic.utils.formatting import RuffNotFoundError, format_with_ruff
from supabase_pydantic.utils.io import get_working_directories

# Option groups
generator_config = OptionGroup('Generator Options', help='Options for generating code.')

# Option groups for connection sources
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


@click.command(short_help='Generates code with specified configurations.')  # noqa
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
    '--disable-model-prefix-protection',
    is_flag=True,
    show_default=True,
    default=False,
    help='Disable Pydantic\'s "model_" prefix protection to allow fields with "model_" prefix without aliasing.',
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
    disable_model_prefix_protection: bool = False,
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
    table_dict = construct_tables(
        conn_type=conn_type,
        schemas=schemas,
        disable_model_prefix_protection=disable_model_prefix_protection,
        **env_vars,
    )

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
                disable_model_prefix_protection=disable_model_prefix_protection,
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
