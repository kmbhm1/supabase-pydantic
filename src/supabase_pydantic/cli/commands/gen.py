import logging
import os
import re
from typing import Any

import click
from click_option_group import OptionGroup, RequiredMutuallyExclusiveOptionGroup

from src.supabase_pydantic.cli.common import check_readiness, config_dict, framework_choices, model_choices
from src.supabase_pydantic.core.writers.factories import FileWriterFactory

# Move construct_tables import to function scope to allow patching in tests
from src.supabase_pydantic.db.constants import POSTGRES_SQL_CONN_REGEX, DatabaseConnectionType, WriterConfig

# Move seed functions to function scope to allow patching in tests
from src.supabase_pydantic.utils.config import get_standard_jobs
from src.supabase_pydantic.utils.formatting import format_with_ruff
from src.supabase_pydantic.utils.io import get_working_directories
from src.supabase_pydantic.utils.types import local_default_env_configuration

generator_config = OptionGroup('Generator Options', help='Options for generating code.')
connect_sources = RequiredMutuallyExclusiveOptionGroup('Connection Configuration', help='The sources of the input data')


@click.command('gen', short_help='Generates code from a database.')
@click.option(
    '-m',
    '--model',
    'models',
    multiple=True,
    type=click.Choice(model_choices, case_sensitive=False),
    default=model_choices,
    help='The type of model to generate.',
    show_default=True,
)
@click.option(
    '-f',
    '--framework',
    'frameworks',
    multiple=True,
    type=click.Choice(framework_choices, case_sensitive=False),
    default=framework_choices,
    help='The framework to generate models for.',
    show_default=True,
)
@click.option(
    '-d',
    '--directory',
    'default_directory',
    default=config_dict.get('default_directory', 'entities'),
    help='The directory to generate models in.',
    show_default=True,
)
@click.option(
    '-o',
    '--overwrite',
    is_flag=True,
    help='Overwrite existing files.',
)
@click.option(
    '--null-parent-classes',
    is_flag=True,
    help='Add `None` to parent classes. For example, `class Foo(Bar | None)` instead of `class Foo(Bar)`.',
)
@click.option(
    '--seed-data',
    'create_seed_data',
    is_flag=True,
    help='Generate seed data.',
)
@click.option(
    '--all-schemas',
    is_flag=True,
    help='Generate models for all available schemas.',
)
@click.option(
    '-s',
    '--schema',
    multiple=True,
    default=('public',),
    help='Generate models for specific schemas. Can be used multiple times.',
    show_default=True,
)
@connect_sources.option(
    '--local',
    is_flag=True,
    help='Use local database connection.',
)
@connect_sources.option(
    '--db-url',
    'db_url',
    type=str,
    help='Use connection URL for database.',
)
@generator_config.option(
    '--no-crud',
    'no_crud_models',
    is_flag=True,
    help='Do not generate CRUD models.',
)
@generator_config.option(
    '--no-enums',
    'no_enums',
    is_flag=True,
    help='Do not generate enums.',
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug mode.',
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
    # Set up logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    # Log the configuration
    if debug:
        logging.debug(f'model_choices: {model_choices}')
        logging.debug(f'framework_choices: {framework_choices}')
        logging.debug(f'models: {models}')
        logging.debug(f'frameworks: {frameworks}')
        logging.debug(f'default_directory: {default_directory}')
        logging.debug(f'overwrite: {overwrite}')
        logging.debug(f'null_parent_classes: {null_parent_classes}')
        logging.debug(f'create_seed_data: {create_seed_data}')
        logging.debug(f'all_schemas: {all_schemas}')
        logging.debug(f'schema: {schema}')
        logging.debug(f'local: {local}')
        logging.debug(f'db_url: {db_url}')
        logging.debug(f'no_crud_models: {no_crud_models}')
        logging.debug(f'no_enums: {no_enums}')
        logging.debug(f'debug: {debug}')

    # Set up database connection configuration
    conn_type = DatabaseConnectionType.LOCAL
    env_vars: dict[str, Any] = {}
    if db_url is not None:
        # Check if the database URL is valid
        if re.match(POSTGRES_SQL_CONN_REGEX, db_url) is None:
            print(f'Invalid database URL: "{db_url}". Exiting.')
            return
        print('Checking local database connection')
        conn_type = DatabaseConnectionType.DB_URL
        env_vars['DB_URL'] = db_url

    # Handle local connection
    if local:
        conn_type = DatabaseConnectionType.LOCAL
        env_vars = dict(
            {
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
    # Import construct_tables here to allow patching in tests
    from src.supabase_pydantic.db.connection import construct_tables

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
    try:
        for p in paths:
            format_with_ruff(p)
            logging.info(f'File formatted successfully: {p}')
    except Exception as e:
        logging.error('An error occurred while running ruff:')
        logging.error(str(e))

    # Generate seed data
    if create_seed_data:
        logging.info('Generating seed data...')
        for s, j in jobs.items():  # s = schema, j = jobs
            # Generate seed data
            tables = table_dict[s]
            # Import seed generation functions here to allow patching in tests
            from src.supabase_pydantic.db.seed.generator import generate_seed_data

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
            # Import write_seed_file here to allow patching in tests
            from src.supabase_pydantic.db.seed.generator import write_seed_file

            fpaths = write_seed_file(seed_data, fname, overwrite)
            print(f'Seed data generated successfully: {", ".join(fpaths)}')
