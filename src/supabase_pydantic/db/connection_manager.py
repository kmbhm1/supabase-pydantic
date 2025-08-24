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

# Get Logger
logger = logging.getLogger(__name__)


_ENV_KEYS = ('DB_NAME', 'DB_USER', 'DB_PASS', 'DB_HOST', 'DB_PORT', 'DB_URL')


def _load_dotenv_if_any(env_file: str | None) -> None:
    """Load environment variables from .env file if specified or find default."""
    dotenv_path = env_file or find_dotenv(usecwd=True)
    if dotenv_path:
        logger.debug(f'Loading environment variables from {dotenv_path}')
        load_dotenv(dotenv_path)
    else:
        logger.debug('No .env file found, using system environment variables')


def _collect_from_environment() -> dict[str, Any]:
    """Collect environment variables from .env file if specified or find default."""
    return {k: os.getenv(k) for k in _ENV_KEYS}


def _normalize_overrides(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Map kwargs into DB_* env keys; support db_url specially."""
    out: dict[str, Any] = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        key = 'DB_URL' if k.lower() == 'db_url' else f'DB_{k.upper()}'
        out[key] = v
    return out


def _required_vars(conn_type: DatabaseConnectionType) -> list[str]:
    """Return required environment variables based on connection type."""
    return ['DB_URL'] if conn_type == DatabaseConnectionType.DB_URL else ['DB_NAME', 'DB_USER', 'DB_PASS', 'DB_HOST']


def _fill_missing_with_local_defaults(
    env_vars: dict[str, Any],
    db_type: DatabaseType,
) -> dict[str, Any]:
    """Fill only missing keys from local defaults; do not overwrite provided ones."""
    defaults = local_default_env_configuration(db_type)
    merged = env_vars.copy()
    for k, v in defaults.items():
        if merged.get(k) in (None, ''):
            merged[k] = v
    return merged


def _mask(params: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive information in connection parameters."""
    masked = params.copy()
    if masked.get('password'):
        masked['password'] = '******'
    if masked.get('db_url'):
        masked['db_url'] = '******'
    return masked


def setup_database_connection(
    conn_type: DatabaseConnectionType,
    db_type: DatabaseType | None = None,
    env_file: str | None = None,
    local: bool = False,
    db_url: str | None = None,
    **kwargs: Any,
) -> tuple[PostgresConnectionParams | MySQLConnectionParams, DatabaseType]:
    """Set up database connection parameters from environment variables or direct inputs.

    Precedence: explicit db_url arg > kwargs > OS env (+ .env).
    """
    # 1) ingest config sources
    _load_dotenv_if_any(env_file)
    env_vars = _collect_from_environment()

    # 2) apply kwargs overrides (db_url handled specially)
    env_vars.update(_normalize_overrides(kwargs))

    # 3) explicit db_url arg wins over everything
    if db_url:
        env_vars['DB_URL'] = db_url

    # 4) required fields present?
    required = _required_vars(conn_type)
    missing = [k for k in required if not env_vars.get(k)]
    if missing:
        if local:
            # ensure db_type is set before defaults, default to POSTGRES
            db_type = db_type or DatabaseType.POSTGRES
            logger.info(f'Using default local connection values for {db_type.value.lower()}')
            env_vars = _fill_missing_with_local_defaults(env_vars, db_type)
            # re-check after filling
            missing = [k for k in required if not env_vars.get(k)]
        if missing:
            raise ValueError(f'Missing required connection variables: {", ".join(missing)}')

    # 5) database type resolution
    if db_type is None and env_vars.get('DB_URL'):
        detected = detect_database_type(env_vars['DB_URL'])
        if detected:
            db_type = detected
            logger.info(f'Auto-detected database type: {db_type.value}')
    if db_type is None:
        db_type = DatabaseType.POSTGRES
        logger.info(f'No database type specified, using default: {db_type.value}')

    # 6) map to connector params (drop Nones)
    conn_params_dict = {
        'dbname': env_vars.get('DB_NAME'),
        'user': env_vars.get('DB_USER'),
        'password': env_vars.get('DB_PASS'),
        'host': env_vars.get('DB_HOST'),
        'port': env_vars.get('DB_PORT'),
        'db_url': env_vars.get('DB_URL'),
    }
    conn_params_dict = {k: v for k, v in conn_params_dict.items() if v is not None}

    logger.debug(f'Connection parameters: {_mask(conn_params_dict)}')

    # 7) construct typed params via your factory
    connection_params = ConnectionParamFactory.create_connection_params(conn_params_dict, db_type)
    return connection_params, db_type
