"""MySQL database connector implementation."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import mysql.connector
from mysql.connector.connection import MySQLConnection

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.models import MySQLConnectionParams

# Get Logger
logger = logging.getLogger(__name__)


class MySQLConnector(BaseDBConnector):
    """MySQL database connector implementation."""

    def __init__(
        self,
        connection_params: dict[str, Any] | MySQLConnectionParams | None = None,
        **kwargs: Any,
    ):
        """Initialize MySQL connector with connection parameters.

        Args:
            connection_params: Connection parameters as Pydantic model or dictionary
            **kwargs: Additional connection parameters
        """
        # Set default connection parameters if none provided
        if connection_params is None:
            connection_params = {}

        # Convert Pydantic model to dictionary if needed
        if isinstance(connection_params, MySQLConnectionParams):
            self.connection_params = connection_params.to_dict()
        else:
            self.connection_params = connection_params

        # Update with additional kwargs
        self.connection_params.update({k: v for k, v in kwargs.items() if v is not None})

        # Store a copy of the connection parameters without the password for logging
        self.masked_params = self.connection_params.copy()
        if 'password' in self.masked_params:
            self.masked_params['password'] = '******'
        if 'db_url' in self.masked_params:
            self.masked_params['db_url'] = '******'

        logger.debug(f'MySQL connection parameters initialized: {self.masked_params}')

    def connect(self) -> MySQLConnection:  # type: ignore
        """Create a new database connection.

        Returns:
            A new database connection.

        Raises:
            ConnectionError: If the connection fails.
        """
        try:
            # Connect using database URL if available
            if 'db_url' in self.connection_params and self.connection_params['db_url'] is not None:
                db_url = self.connection_params['db_url']
                logger.info('Connecting to MySQL using database URL')

                # Parse URL parameters
                url_params = self.get_url_connection_params(db_url)
                connection = mysql.connector.connect(**url_params)
            else:
                # Connect using direct parameters
                logger.info('Connecting to MySQL using direct connection parameters')
                conn_params = {
                    'user': self.connection_params.get('user'),
                    'password': self.connection_params.get('password'),
                    'host': self.connection_params.get('host', 'localhost'),
                    'port': int(self.connection_params.get('port', 3306)),
                    'database': self.connection_params.get('dbname'),
                }

                # Remove None values
                conn_params = {k: v for k, v in conn_params.items() if v is not None}
                connection = mysql.connector.connect(**conn_params)

            logger.info('MySQL connection established successfully')
            return connection  # type: ignore

        except Exception as e:
            logger.error(f'MySQL connection failed: {str(e)}')
            if logger.getEffectiveLevel() <= logging.DEBUG:
                raise ConnectionError(f'Failed to connect to MySQL database: {str(e)}')

    @contextmanager
    def __call__(self) -> Generator[MySQLConnection, None, None]:
        """Context manager for database connection.

        Yields:
            MySQL connection object
        """
        connection = self.connect()
        try:
            yield connection
        finally:
            self.close_connection(connection)

    def __enter__(self) -> MySQLConnection:
        """Enter context manager.

        Returns:
            MySQL connection object
        """
        self._connection = self.connect()
        return self._connection

    def __exit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Exit context manager.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        if hasattr(self, '_connection'):
            self.close_connection(self._connection)
            delattr(self, '_connection')

    def check_connection(self, connection: MySQLConnection | None = None) -> bool:
        """Check if the database connection is valid.

        Args:
            connection: Optional connection object to check

        Returns:
            True if the connection is valid, False otherwise
        """
        try:
            # Always create a new test connection
            test_connection = None
            try:
                test_connection = self.connect()
                if test_connection is None:
                    logger.error('MySQL connection failed: Could not establish connection to server')
                    return False

                cursor = test_connection.cursor()
                cursor.execute('SELECT 1')
                cursor.fetchone()
                cursor.close()
                return True
            finally:
                if test_connection is not None:
                    self.close_connection(test_connection)

        except Exception as e:
            if "'NoneType' object has no attribute 'cursor'" in str(e):
                logger.error('MySQL connection failed: Could not establish connection to server')
            else:
                logger.error(f'Connection check failed: {str(e)}')
            return False

    def close_connection(self, conn: MySQLConnection) -> None:
        """Close the database connection.

        Args:
            conn: MySQL connection object.
        """
        if conn and hasattr(conn, 'is_connected') and conn.is_connected():
            conn.close()
            logger.debug('MySQL connection closed')

    def execute_query(self, conn: MySQLConnection, query: str, params: tuple = ()) -> list[tuple[Any, ...]]:
        """Execute a query and return results.

        Args:
            conn: MySQL connection object.
            query: SQL query to execute.
            params: Parameters for the SQL query.

        Returns:
            List of result rows as tuples.
        """
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            return list(results)  # Ensure we return the correct type
        except Exception as e:
            logger.error(f'Error executing query: {str(e)}')
            raise
        finally:
            cursor.close()

    def get_url_connection_params(self, url: str) -> dict[str, Any]:
        """Parse connection URL into parameters.

        Args:
            url: Database connection URL.

        Returns:
            Dictionary of connection parameters.

        Raises:
            ValueError: If URL is invalid or cannot be parsed.
        """
        try:
            from urllib.parse import unquote_plus, urlparse

            # Log masked URL for debugging
            masked_url = url.replace(url.split('@')[0], '******@') if '@' in url else url
            logger.debug(f'Parsing connection URL: {masked_url}')

            parsed_url = urlparse(url)

            if not parsed_url.scheme or parsed_url.scheme.lower() != 'mysql':
                raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}, expected 'mysql'")

            # Extract user and password
            user = parsed_url.username or ''
            password = unquote_plus(parsed_url.password) if parsed_url.password else ''

            # Extract host and port
            host = parsed_url.hostname or 'localhost'
            port = parsed_url.port or 3306

            # Extract database name
            path = parsed_url.path
            if path.startswith('/'):
                path = path[1:]
            database = path

            params = {
                'user': user,
                'password': password,
                'host': host,
                'port': port,
                'database': database,
            }

            # Log the connection parameters (masking sensitive data)
            masked_params = {**params}
            if 'password' in masked_params:
                masked_params['password'] = '******'
            logger.debug(f'Parsed connection parameters: {masked_params}')

            return params
        except Exception as e:
            logger.error(f'Error parsing connection URL: {str(e)}')
            raise ValueError(f'Invalid MySQL connection URL: {str(e)}')

    def validate_connection_params(self, params: dict[str, Any] | MySQLConnectionParams) -> MySQLConnectionParams:
        """Validate and convert connection parameters to the appropriate Pydantic model.

        Args:
            params: Connection parameters as a Pydantic model or dict

        Returns:
            Validated connection parameters as a Pydantic model

        Raises:
            ValueError: If connection parameters are invalid
        """
        # If it's already a Pydantic model, return it
        if isinstance(params, MySQLConnectionParams):
            return params

        # Convert dict to Pydantic model
        try:
            if 'db_url' in params and params['db_url']:
                # Parse URL and validate components
                url_params = self.get_url_connection_params(params['db_url'])

                # Map 'database' to 'dbname' if needed
                if 'database' in url_params:
                    url_params['dbname'] = url_params.pop('database')

                # Ensure port is a string
                if 'port' in url_params and not isinstance(url_params['port'], str):
                    url_params['port'] = str(url_params['port'])

                # Merge URL params with original params, prioritizing URL values
                merged_params = {**params, **url_params}
                return MySQLConnectionParams(**merged_params)
            else:
                # Validate direct connection parameters
                required_params = ['user', 'host']
                missing = [param for param in required_params if param not in params or not params[param]]

                if missing:
                    raise ValueError(f'Missing required connection parameters: {", ".join(missing)}')

                return MySQLConnectionParams(**params)
        except Exception as e:
            logger.error(f'Error validating connection parameters: {str(e)}')
            raise ValueError(f'Invalid MySQL connection parameters: {str(e)}')
