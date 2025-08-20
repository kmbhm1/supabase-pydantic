"""Connection manager for database operations."""

import logging
import os
from typing import Any

from dotenv import find_dotenv, load_dotenv

from supabase_pydantic.core.config import local_default_env_configuration
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factories.connection_factory import ConnectionParamFactory
from supabase_pydantic.db.models import MySQLConnectionParams, PostgresConnectionParams
from supabase_pydantic.db.utils.url_parser import detect_database_type

logger = logging.getLogger(__name__)


def setup_database_connection(
    conn_type: DatabaseConnectionType,
    db_type: DatabaseType | None = None,
    env_file: str | None = None,
    local: bool = False,
    **kwargs: Any,
) -> tuple[PostgresConnectionParams | MySQLConnectionParams, DatabaseType]:
    """Set up database connection parameters from environment variables.

    Args:
        conn_type: Connection type (LOCAL or DB_URL)
        db_type: Database type (POSTGRES or MYSQL), or None to auto-detect
        env_file: Path to .env file, or None to use default
        local: Whether to use local default values if env vars are missing
        **kwargs: Additional parameters to override environment variables

    Returns:
        Tuple of (connection parameters object, database type)

    Raises:
        ValueError: If database connection parameters are invalid
    """
    env_vars: dict[str, Any] = {}

    # Load environment variables
    try:
        # Try to load from .env file if specified or find default
        if env_file:
            dotenv_path = env_file
        else:
            dotenv_path = find_dotenv(usecwd=True)

        if dotenv_path:
            logger.debug(f'Loading environment variables from {dotenv_path}')
            load_dotenv(dotenv_path)
        else:
            logger.debug('No .env file found, using system environment variables')

        # Get database connection parameters from environment
        env_vars.update(
            **{
                'DB_NAME': os.environ.get('DB_NAME', None),
                'DB_USER': os.environ.get('DB_USER', None),
                'DB_PASS': os.environ.get('DB_PASS', None),
                'DB_HOST': os.environ.get('DB_HOST', None),
                'DB_PORT': os.environ.get('DB_PORT', None),
                'DB_URL': os.environ.get('DB_URL', None),
            }
        )

        # Override with any directly provided parameters
        for k, v in kwargs.items():
            if v is not None:
                # Special case for db_url to avoid DB_DB_URL
                if k == 'db_url':
                    env_vars['DB_URL'] = v
                else:
                    env_var_key = f'DB_{k.upper()}'
                    env_vars[env_var_key] = v

        # Check for missing environment variables and use defaults if local mode
        missing_vars = [k for k, v in env_vars.items() if v is None]
        if missing_vars:
            logger.warning(f'Missing environment variables: {", ".join(missing_vars)}')
            if local:
                logger.info('Using default local connection values')
                env_vars = local_default_env_configuration()
                logger.debug('Default connection: localhost:5432, database: postgres, user: postgres')
            else:
                logger.error('Environment variables required but not found')
                raise ValueError('Database connection configuration is incomplete')

        # Validate based on connection type
        if conn_type == DatabaseConnectionType.DB_URL and env_vars.get('DB_URL') is None:
            logger.error('DB_URL is required for DB_URL connection type')
            raise ValueError('DB_URL is required for DB_URL connection type')
        elif conn_type == DatabaseConnectionType.LOCAL and not all(
            [env_vars.get('DB_NAME'), env_vars.get('DB_USER'), env_vars.get('DB_PASS'), env_vars.get('DB_HOST')]
        ):
            logger.error('DB_NAME, DB_USER, DB_PASS, and DB_HOST are required for LOCAL connection type')
            raise ValueError('Incomplete database connection parameters')

    except Exception as e:
        logger.error(f'Error setting up database connection: {str(e)}')
        raise

    # Map environment variable names to connector parameter names
    conn_params_dict = {
        'dbname': env_vars.get('DB_NAME'),
        'user': env_vars.get('DB_USER'),
        'password': env_vars.get('DB_PASS'),
        'host': env_vars.get('DB_HOST'),
        'port': env_vars.get('DB_PORT'),
        'db_url': env_vars.get('DB_URL'),
    }

    # Log masked connection parameters (hide sensitive info)
    masked_params = conn_params_dict.copy()
    if masked_params.get('password'):
        masked_params['password'] = '******'
    if masked_params.get('db_url'):
        masked_params['db_url'] = '******'
    logger.info(f'Connection parameters: {masked_params}')

    # Remove None values to avoid passing empty parameters
    conn_params_dict = {k: v for k, v in conn_params_dict.items() if v is not None}

    # Auto-detect database type if not specified and using DB_URL
    if db_type is None and conn_params_dict.get('db_url'):
        detected_db_type = detect_database_type(conn_params_dict['db_url'])
        if detected_db_type:
            db_type = detected_db_type
            logger.info(f'Auto-detected database type: {db_type.value}')

    # Default to PostgreSQL for backward compatibility
    if db_type is None:
        db_type = DatabaseType.POSTGRES
        logger.info(f'No database type specified, using default: {db_type.value}')

    # Create connection parameters object
    connection_params = ConnectionParamFactory.create_connection_params(conn_params_dict, db_type)

    return connection_params, db_type
