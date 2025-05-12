"""Command to generate models from database schemas."""

import logging
import os

import click
from click_option_group import OptionGroup, RequiredMutuallyExclusiveOptionGroup, optgroup

from src.supabase_pydantic.core.utils import (
    check_readiness,
    format_with_ruff,
    generate_seed_data,
    get_standard_jobs,
    get_working_directories,
    local_default_env_configuration,
    write_seed_file,
)
from src.supabase_pydantic.db import AdapterFactory, DatabaseType
from src.supabase_pydantic.utils import FileWriterFactory

# Configure the CLI command groups
generator_config = OptionGroup('Generator Options', help='Options for generating code.')
connect_sources = RequiredMutuallyExclusiveOptionGroup('Connection Configuration', help='The sources of the input data')


@click.command('generate', short_help='Generate models from a database schema.')
@click.argument('models', type=click.Choice(['pydantic']), nargs=-1, required=True)
@click.argument('frameworks', type=click.Choice(['fastapi']), nargs=-1, required=True)
@connect_sources.option(
    '--db-url',
    type=str,
    help='Database connection URL (e.g., postgresql://user:pass@host:port/db)',
    envvar='DB_URL',
)
@connect_sources.option(
    '--local',
    is_flag=True,
    help='Use local database connection from environment variables.',
)
@generator_config.option(
    '-d',
    '--dir',
    '--directory',
    'default_directory',
    default='entities',
    required=False,
    help='The directory to output generated files to. Defaults to "entities".',
)
@generator_config.option(
    '--overwrite',
    is_flag=True,
    default=False,
    help='Overwrite existing files.',
)
@generator_config.option(
    '--null-parent-classes',
    '--nullify-base-schema',
    is_flag=True,
    default=False,
    help='Nullify base schema fields in parent classes.',
)
@generator_config.option(
    '--create-seed-data',
    is_flag=True,
    default=False,
    help='Create seed data for the generated models.',
)
@generator_config.option(
    '--all-schemas',
    is_flag=True,
    default=False,
    help='Generate models for all schemas.',
)
@generator_config.option(
    '--schema',
    multiple=True,
    default=('public',),
    help='Specify schemas to generate models for. Defaults to "public".',
)
@generator_config.option(
    '--no-crud-models',
    is_flag=True,
    default=False,
    help='Do not generate CRUD models.',
)
@generator_config.option(
    '--no-enums',
    is_flag=True,
    default=False,
    help='Do not generate enum types.',
)
@generator_config.option(
    '--debug',
    is_flag=True,
    default=False,
    help='Enable debug logging.',
)
@optgroup(connect_sources)
@optgroup(generator_config)
def gen(
    models: tuple[str, ...],
    frameworks: tuple[str, ...],
    default_directory: str,
    overwrite: bool,
    null_parent_classes: bool,
    create_seed_data: bool,
    all_schemas: bool,
    schema: tuple[str, ...],
    local: bool = False,
    db_url: str | None = None,
    no_crud_models: bool = False,
    no_enums: bool = False,
    debug: bool = False,
) -> None:
    """Generate models from a database schema.

    MODELS: The ORM model type to generate (currently only supports 'pydantic')

    FRAMEWORKS: The framework to generate models for (currently only supports 'fastapi')
    """
    # Set up logging
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    # Determine connection type
    if db_url:
        logging.info(f'Using database URL: {db_url[:10]}...')
        # Create database adapter from URL
        adapter = AdapterFactory.create_from_url(db_url)

    elif local:
        logging.info('Using local database connection from environment variables')
        # Get local connection parameters from environment variables
        env_vars = {
            'DB_NAME': os.environ.get('DB_NAME', None),
            'DB_USER': os.environ.get('DB_USER', None),
            'DB_PASS': os.environ.get('DB_PASS', None),
            'DB_HOST': os.environ.get('DB_HOST', None),
            'DB_PORT': os.environ.get('DB_PORT', None),
        }

        if any(v is None for v in env_vars.values()):
            # Use default local configuration if environment variables are missing
            logging.warning(
                f'Critical environment variables not set: {", ".join(k for k, v in env_vars.items() if v is None)}.'
            )
            logging.info('Using default local values...')
            env_vars = local_default_env_configuration()

        # Ensure environment variables are set correctly
        if not check_readiness(env_vars):
            click.echo('Error: Database connection environment variables are not set correctly')
            return

        # Create database adapter with local connection parameters
        adapter = AdapterFactory.create_adapter(DatabaseType.POSTGRES, **env_vars)
    else:
        click.echo('Error: No database connection method specified')
        return

    # Get the directories for the generated files
    dirs = get_working_directories(default_directory, frameworks, auto_create=True)

    # Get the database schema and table details
    try:
        # Determine schemas to process
        schemas_to_process = ('*',) if all_schemas else tuple(schema)

        # Connect to database and get schema info
        with adapter:
            if all_schemas:
                # Get all available schemas
                all_schema_names = adapter.get_schemas()
                logging.info(f'Found schemas: {", ".join(all_schema_names)}')

            # Process each schema
            table_dict = {}
            for schema_name in schemas_to_process if schemas_to_process != ('*',) else all_schema_names:
                logging.info(f'Processing schema: {schema_name}')
                tables = adapter.construct_table_info(schema_name)
                if tables:
                    table_dict[schema_name] = tables
                else:
                    logging.warning(f'No tables found in schema: {schema_name}')
    except Exception as e:
        click.echo(f'Error connecting to database: {e}')
        return

    # Filter out schemas with no tables
    schemas_with_no_tables = [k for k, v in table_dict.items() if not v]
    if schemas_with_no_tables:
        logging.warning(
            f'The following schemas have no tables and will be skipped: {", ".join(schemas_with_no_tables)}'
        )

    table_dict = {k: v for k, v in table_dict.items() if v}
    schemas = tuple(table_dict.keys())

    if not schemas:
        click.echo('No schemas with tables found. Exiting...')
        return

    # Configure the writer jobs
    std_jobs = get_standard_jobs(models, frameworks, dirs, schemas)
    jobs = {}
    for k, v in std_jobs.items():
        jobs[k] = {}
        for job, c in v.items():
            if c.enabled is False:
                continue
            jobs[k][job] = c

    # Generate the models
    paths = []
    factory = FileWriterFactory()

    for s, j in jobs.items():  # s = schema, j = jobs
        tables = table_dict[s]
        for job, c in j.items():  # c = config
            logging.info(f'Generating {job} models for schema {s}...')
            writer = factory.get_file_writer(
                tables,
                c.fpath(),
                c.file_type,
                c.framework_type,
                add_null_parent_classes=null_parent_classes,
                generate_crud_models=not no_crud_models,
                generate_enums=not no_enums,
            )

            # Save the generated models
            p, vf = writer.save(overwrite)
            paths += [p, vf] if vf is not None else [p]
            logging.info(f"{job} models generated successfully for schema '{s}': {p}")

    # Format the generated files with ruff
    try:
        for p in paths:
            format_with_ruff(p)
            logging.info(f'File formatted successfully: {p}')
    except Exception as e:
        logging.error(f'An error occurred while formatting files: {e}')

    # Generate seed data if requested
    if create_seed_data:
        logging.info('Generating seed data...')
        for s, j in jobs.items():  # s = schema, j = jobs
            # Generate seed data
            tables = table_dict[s]
            seed_data = generate_seed_data(tables)

            # Check if seed data was generated
            if not seed_data:
                logging.warning(f'Failed to generate seed data for schema: {s}')
                if all(t.table_type == 'VIEW' for t in tables):
                    logging.info('All entities are views in this schema. Skipping seed data generation...')
                else:
                    logging.error('Unknown error occurred; check the schema. Skipping seed data generation...')
                continue

            # Write the seed data
            d = dirs.get('default')
            fname = os.path.join(d if d is not None else 'entities', f'seed_{s}.sql')
            fpaths = write_seed_file(seed_data, fname, overwrite)
            logging.info(f'Seed data generated successfully: {", ".join(fpaths)}')

    click.echo(f'Successfully generated {len(paths)} files in {default_directory}')
