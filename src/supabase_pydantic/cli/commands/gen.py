import logging
import os
from urllib.parse import urlparse

import click
from click_option_group import OptionGroup, RequiredMutuallyExclusiveOptionGroup

from supabase_pydantic.cli.common import (
    framework_choices,
    model_choices,
)
from supabase_pydantic.core.config import WriterConfig, get_standard_jobs
from supabase_pydantic.core.writers.factories import FileWriterFactory
from supabase_pydantic.db.builder import construct_tables
from supabase_pydantic.db.connection_manager import setup_database_connection
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import MySQLConnectionParams
from supabase_pydantic.db.seed import generate_seed_data, write_seed_file
from supabase_pydantic.utils.formatting import RuffNotFoundError, format_with_ruff
from supabase_pydantic.utils.io import get_working_directories
from supabase_pydantic.utils.logging import setup_logging

# Get Logger
logger = logging.getLogger(__name__)

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

# Helper Functions


_LEVEL_NAME_TO_NUM = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG,
    # Optional “TRACE” convenience; Loguru uses 5 by default. Stdlib will treat it like DEBUG-1.
    'TRACE': 5,
}


def _resolve_level(log_level: str | None, debug: bool, verbose: int, quiet: int) -> int:
    """
    Priority (highest wins):
      1) --log-level
      2) -v / -q adjustments
      3) --debug
      4) default INFO
    """  # noqa: D205, D212, D415
    if log_level:
        return _LEVEL_NAME_TO_NUM[log_level.upper()]

    # Base from --debug or INFO
    base = logging.DEBUG if debug else logging.INFO

    # Apply -v / -q deltas: each -v lowers the numeric value (more verbose),
    # each -q raises it (less verbose). Step size ≈ one stdlib level.
    # INFO(20) + quiet*10 - verbose*10
    candidate = base + (quiet * 10) - (verbose * 10)

    # Clamp to valid range
    candidate = max(_LEVEL_NAME_TO_NUM['TRACE'], min(candidate, logging.CRITICAL))
    return candidate


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
    '--db-type',
    type=click.Choice(['postgres', 'mysql']),
    help='Specify the database type explicitly (postgres or mysql).',
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
    flag_value=False,
    default=True,
    show_default=True,
    help='Disable overwriting of existing files.',
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
    '--singular-names',
    is_flag=True,
    show_default=True,
    default=False,
    help='Generate class names in singular form (e.g., "Product" instead of "Products" for table "products").',
)
@click.option(
    '--log-level',
    type=click.Choice(['critical', 'error', 'warning', 'info', 'debug', 'trace'], case_sensitive=False),
    default=None,
    help='Set the log level explicitly (overrides --debug/-v/-q).',
)
@click.option(
    '-v',
    '--verbose',
    count=True,
    help='Increase verbosity (e.g., -v → INFO, -vv → DEBUG).',
)
@click.option(
    '-q',
    '--quiet',
    count=True,
    help='Decrease verbosity (e.g., -q → WARNING, -qq → ERROR).',
)
@click.option(
    '--debug/--no-debug',
    is_flag=True,
    default=False,
    help='Enable debug logging (kept for compatibility; overridden by --log-level).',
)
@click.option(
    '--log-timefmt',
    default='YYYY-MM-DD HH:mm:ss',  # Changed from 'HH:mm:ss'
    show_default=True,
    help='Loguru time format (e.g., "YYYY-MM-DD HH:mm:ss", "MM-DD HH:mm:ss").',
)
@click.option(
    '--datefmt',
    default='%Y-%m-%d %H:%M:%S',  # Changed from '%H:%M:%S'
    show_default=True,
    help='Stdlib time format (strftime), e.g., "%Y-%m-%d %H:%M:%S").',
)
@click.option(
    '--log-ms/--no-log-ms',
    default=False,
    show_default=True,
    help='Append milliseconds to timestamps.',
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
    db_url: str | None = None,
    db_type: str | None = None,
    no_crud_models: bool = False,
    no_enums: bool = False,
    disable_model_prefix_protection: bool = False,
    singular_names: bool = False,
    # NEW / UPDATED:
    log_level: str | None = None,
    verbose: int = 0,
    quiet: int = 0,
    debug: bool = False,
    log_timefmt: str = 'YYYY-MM-DD HH:mm:ss',
    datefmt: str = '%Y-%m-%d %H:%M:%S',
    log_ms: bool = False,
) -> None:
    """Generate models from a database."""
    # logging setup
    effective_level = _resolve_level(log_level, debug, verbose, quiet)

    setup_logging(
        level=effective_level,
        loguru_timefmt=log_timefmt,
        stdlib_datefmt=datefmt,
        include_ms=log_ms,
        force=True,  # reliably override any pre-configured handlers
    )

    # example: reflect the resolved level
    logger.debug(
        f'Logging configured: level={effective_level} '
        f'({logging.getLevelName(effective_level)}), '
        f'timefmt={log_timefmt}/{datefmt}, ms={log_ms}'
    )

    # validate connection options and prepare environment variables
    if not local and db_url is None:
        logger.error('Please provide a valid connection source (--local or --db-url). Exiting...')
        return

    # setup database connection
    try:
        # Convert db_type string to DatabaseType enum if provided
        database_type = None
        if db_type:
            if db_type.lower() == 'postgres':
                database_type = DatabaseType.POSTGRES
            elif db_type.lower() == 'mysql':
                database_type = DatabaseType.MYSQL
            else:
                logger.error(f'Unsupported database type: {db_type}')
                return
            logger.info(f'Using specified database type: {database_type.value}')

        # Set up the database connection using our connection manager
        conn_type = DatabaseConnectionType.DB_URL if db_url else DatabaseConnectionType.LOCAL
        connection_params, detected_db_type = setup_database_connection(
            conn_type=conn_type, db_type=database_type, env_file=None, local=local, db_url=db_url
        )

        logger.info(f'Successfully established connection parameters for {detected_db_type.value}')

    except Exception as e:
        logger.error(f'Error setting up database connection: {str(e)}')
        return

    # Get the directories for the generated files
    dirs = get_working_directories(default_directory, frameworks, auto_create=True)

    # Determine schemas to process
    schemas = ('*',) if all_schemas else tuple(schema)  # Use '*' as an indicator to fetch all schemas

    # For MySQL, the default schema is the database name, not 'public'
    if detected_db_type == DatabaseType.MYSQL and schemas == ('public',):
        # If using DB_URL, extract database name from connection parameters
        if conn_type == DatabaseConnectionType.DB_URL and connection_params.db_url is not None:
            # Debug log original connection params
            logger.debug(f'MySQL connection parameters before URL parsing: dbname={connection_params.dbname}')

            parsed_url_debug = urlparse(connection_params.db_url)
            logger.debug(f'MySQL db_url path: {parsed_url_debug.path}')

            # For MySQL, we need to use the database name as the schema
            if isinstance(connection_params, MySQLConnectionParams):
                # Parse the database name from the URL directly
                db_name = parsed_url_debug.path.strip('/')

                if db_name:
                    schemas = (db_name,)
                    logger.info(
                        f"Using MySQL database name '{schemas[0]}' extracted from URL as schema instead of 'public'"
                    )
                else:
                    schemas = ('*',)
                    logger.info("Using all available MySQL schemas since database name couldn't be determined")
        else:
            # Use extracted dbname if available, otherwise use wildcard
            if isinstance(connection_params, MySQLConnectionParams) and connection_params.dbname:
                schemas = (connection_params.dbname,)
                logger.info(f"Using MySQL database name '{schemas[0]}' as schema instead of 'public'")
            else:
                schemas = ('*',)
                logger.info("Using all available MySQL schemas since 'public' doesn't exist in MySQL")

    # Generate table information from the database
    table_dict = construct_tables(
        conn_type=conn_type,
        db_type=detected_db_type,
        schemas=schemas,
        disable_model_prefix_protection=disable_model_prefix_protection,
        connection_params=connection_params.to_dict(),
    )
    if not table_dict:
        logger.warning('Exiting; No table information obtained from the database')
        return

    schemas_with_no_tables = [k for k, v in table_dict.items() if len(v) == 0]
    if len(schemas_with_no_tables) > 0:
        logger.warning(f'The following schemas have no tables and will be skipped: {", ".join(schemas_with_no_tables)}')
    table_dict = {k: v for k, v in table_dict.items() if len(v) > 0}
    if all_schemas:  # Reset schemas if all_schemas is True
        schemas = tuple(table_dict.keys())

    # Configure the writer jobs
    std_jobs = get_standard_jobs(models, frameworks, dirs, schemas)
    jobs: dict[str, dict[str, WriterConfig]] = {}

    # For MySQL, ensure that job configuration includes the actual schema name and not just 'public'
    job_schemas = schemas  # noqa: F841
    if detected_db_type == DatabaseType.MYSQL:
        # Get the actual schema names from table_dict (excluding the synthetic 'public')
        actual_schemas = [s for s in table_dict.keys()]
        if actual_schemas and 'public' in std_jobs:
            logger.info(f'Adjusting job configuration to include MySQL schemas: {", ".join(actual_schemas)}')
            # Create a modified std_jobs that includes actual MySQL schema names
            for schema in actual_schemas:
                if schema not in std_jobs:
                    std_jobs[schema] = std_jobs['public']

    for k, v in std_jobs.items():
        jobs[k] = {}
        for job, c in v.items():
            if c.enabled is False:
                continue
            jobs[k][job] = c

    # Generate the models; Run jobs
    paths = []
    factory = FileWriterFactory()

    # Process each schema
    for s, j in jobs.items():  # s = schema, j = jobs
        # For MySQL, the database name in connection parameters might be different from the schemas found
        # by the database connector. Add a fallback logic.
        schema_key = s
        if s not in table_dict and detected_db_type == DatabaseType.MYSQL:
            # Log available schemas for debugging
            available_schemas = list(table_dict.keys())
            logger.info(f"Schema '{s}' not found in table_dict. Available schemas: {available_schemas}")

            # If there's exactly one schema in the database, use that regardless of name
            if len(table_dict) == 1:
                actual_schema = next(iter(table_dict.keys()))
                logger.info(f"Using the only available schema '{actual_schema}' instead of '{s}'")
                schema_key = actual_schema
            # If the database has a 'public' schema (which is uncommon in MySQL but possible)
            elif 'public' in table_dict and s == 'public':
                logger.info("Using 'public' schema directly.")
                schema_key = 'public'
            # If job is for 'public' but we have a schema with same name as database
            elif (
                s == 'public'
                and isinstance(connection_params, MySQLConnectionParams)
                and connection_params.dbname in table_dict
            ):
                schema_key = connection_params.dbname
                logger.info(f"Using database name '{schema_key}' instead of 'public'")
            # In other cases, try to find a matching schema
            else:
                logger.error(f"Could not find schema '{s}' in available schemas: {available_schemas}")
                continue

        # Get tables for the current schema (using the potentially corrected schema key)
        if schema_key not in table_dict:
            logger.error(f"Schema '{schema_key}' not found in table_dict, skipping")
            continue

        tables = table_dict[schema_key]
        # Sort tables by name
        tables.sort(key=lambda x: x.name)

        # Process each job for the current schema
        for job, c in j.items():  # c = config
            logger.info(f'Generating {job} models...')
            p, vf = factory.get_file_writer(
                tables,
                c.fpath(),
                c.file_type,
                c.framework_type,
                add_null_parent_classes=null_parent_classes,
                generate_crud_models=not no_crud_models,
                generate_enums=not no_enums,
                disable_model_prefix_protection=disable_model_prefix_protection,
                singular_names=singular_names,
                database_type=detected_db_type,
            ).save(overwrite)
            paths += [p, vf] if vf is not None else [p]
            logger.info(f"{job} models generated successfully for schema '{s}': {p}")

    # Format the generated files
    for p in paths:
        try:
            format_with_ruff(p)
            logger.info(f'File formatted successfully: {p}')
        except RuffNotFoundError as e:
            logger.warning(str(e))  # The exception message is already descriptive
        except Exception as e:  # Catch any other unexpected errors during formatting
            logger.error(f'An unexpected error occurred while formatting {p}: {str(e)}')

    # Generate seed data
    if create_seed_data:
        logger.info('Generating seed data...')
        for s, j in jobs.items():  # s = schema, j = jobs
            # Generate seed data
            tables = table_dict[s]
            seed_data = generate_seed_data(tables)

            # Check if seed data was generated
            if len(seed_data) == 0:
                logger.warning(f'Failed to generate seed data for schema: {s}')
                if all([t.table_type == 'VIEW' for t in tables]):
                    logger.info('All entities are views in this schema. Skipping seed data generation...')
                else:
                    logger.error('Unknown error occurred; check the schema. Skipping seed data generation...')
                continue

            # Write the seed data
            d = dirs.get('default')
            fname = os.path.join(d if d is not None else 'entities', f'seed_{s}.sql')
            fpaths = write_seed_file(seed_data, fname, overwrite)
            logger.info(f'Seed data generated successfully: {", ".join(fpaths)}')
