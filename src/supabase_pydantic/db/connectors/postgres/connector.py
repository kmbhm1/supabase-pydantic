"""PostgreSQL database connector implementation."""

import logging
from typing import Any
from urllib.parse import urlparse

import psycopg2

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.models import PostgresConnectionParams

# Get Logger
logger = logging.getLogger(__name__)


class PostgresConnector(BaseDBConnector[PostgresConnectionParams]):
    """PostgreSQL database connector implementation."""

    def __init__(
        self, connection_params: PostgresConnectionParams | dict[str, Any] | None = None, **kwargs: Any
    ) -> None:
        """Initialize the PostgreSQL connector.

        Args:
            connection_params: Connection parameters as a Pydantic model or dict
            **kwargs: Additional parameters passed from the factory
        """
        super().__init__(connection_params, **kwargs)
        # Store the original PostgresConnectionParams object if provided,
        # or create one from the dictionary that was passed to the parent class
        if isinstance(connection_params, PostgresConnectionParams):
            self.connection_params = connection_params
        elif isinstance(connection_params, dict):
            try:
                self.connection_params = PostgresConnectionParams(**connection_params)
            except Exception as e:
                logger.warning(f'Could not create PostgresConnectionParams from dict: {e}')
                self.connection_params = None
        else:
            self.connection_params = None
        logger.debug('PostgresConnector initialized')

    def validate_connection_params(self, params: PostgresConnectionParams | dict[str, Any]) -> PostgresConnectionParams:
        """Validate and convert connection parameters to PostgresConnectionParams.

        Args:
            params: Connection parameters as a Pydantic model or dict

        Returns:
            Validated connection parameters as PostgresConnectionParams

        Raises:
            ValueError: If connection parameters are invalid
        """
        if isinstance(params, PostgresConnectionParams):
            if not params.is_valid():
                raise ValueError(
                    "Invalid connection parameters. Either provide 'db_url' or "
                    "all of 'dbname', 'user', 'password', 'host', 'port'."
                )
            return params

        # Convert dict to model
        try:
            model = PostgresConnectionParams(**params)
            if not model.is_valid():
                raise ValueError(
                    "Invalid connection parameters. Either provide 'db_url' or "
                    "all of 'dbname', 'user', 'password', 'host', 'port'."
                )
            return model
        except Exception as e:
            raise ValueError(f'Invalid connection parameters: {e}')

    def connect(self, connection_params: PostgresConnectionParams | dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Create a connection to the PostgreSQL database.

        Args:
            connection_params: Connection parameters as a Pydantic model or dict
            **kwargs: Additional connection parameters for PostgreSQL.
                May include db_url for URL-based connection or
                dbname, user, password, host, port for direct connection.

        Returns:
            PostgreSQL database connection object.

        Raises:
            ConnectionError: If connection to the database fails.
            ValueError: If required parameters are missing.
        """
        # Merge parameters from different sources with priority:
        # 1. Explicitly provided kwargs
        # 2. connection_params argument
        # 3. Stored connection_params from __init__

        params = {}

        # Start with stored connection params if available
        if self.connection_params:
            params.update(self.connection_params)

        # Update with connection_params if provided
        if connection_params:
            if isinstance(connection_params, dict):
                params.update(connection_params)
            elif isinstance(connection_params, PostgresConnectionParams):
                params.update(connection_params.to_dict())

        # Finally, update with any explicit kwargs
        params.update(kwargs)

        # Log the parameters (hide sensitive info)
        logger.debug(
            'PostgresDBConnector.connect() called with params: %s',
            {k: '***' if k in ('password', 'db_url') else v for k, v in params.items()},
        )

        if 'db_url' in params and params['db_url']:
            logger.info('Using DB_URL connection method')
            return self._create_connection_from_url(params['db_url'])
        elif all(key in params and params[key] for key in ['dbname', 'user', 'password', 'host', 'port']):
            logger.info('Using direct connection method with credentials')
            return self._create_connection(
                params['dbname'],
                params['user'],
                params['password'],
                params['host'],
                params['port'],
            )
        else:
            logger.error('Invalid connection parameters provided')
            raise ValueError(
                "Invalid connection parameters. Either provide 'db_url' or "
                "all of 'dbname', 'user', 'password', 'host', 'port'."
            )

    def check_connection(self, conn: Any = None) -> bool:
        """Check if PostgreSQL connection is active.

        Args:
            conn: PostgreSQL connection object. If not provided, a new connection
                will be created temporarily to check connectivity.

        Returns:
            True if connection is active, False otherwise.
        """
        # If no connection is provided, create a temporary one
        if conn is None:
            try:
                temp_conn = self.connect()
                is_connected = not temp_conn.closed
                self.close_connection(temp_conn)
                logger.info(f'PostgreSQL connection check: {"open" if is_connected else "closed"}')
                return is_connected
            except Exception as e:
                logger.error(f'PostgreSQL connection check failed: {e}')
                return False

        # Check the provided connection
        if conn.closed:
            logger.info('PostgreSQL connection is closed.')
            return False
        else:
            logger.info('PostgreSQL connection is open.')
            return True

    def execute_query(self, conn: Any, query: str, params: tuple = ()) -> list[tuple[Any, ...]]:
        """Execute SQL query and return results.

        Args:
            conn: PostgreSQL connection object
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as tuples.
        """
        cur = conn.cursor()
        try:
            cur.execute(query, params)
            result = cur.fetchall()
            return result if isinstance(result, list) else []
        finally:
            cur.close()

    def close_connection(self, conn: Any) -> None:
        """Close PostgreSQL database connection.

        Args:
            conn: PostgreSQL connection object.
        """
        conn.close()
        logger.info('PostgreSQL connection closed.')

    def get_url_connection_params(self, url: str) -> dict[str, Any]:
        """Parse PostgreSQL connection URL into parameters.

        Args:
            url: PostgreSQL connection URL.

        Returns:
            Dictionary of connection parameters.

        Raises:
            ValueError: If URL is invalid or cannot be parsed.
        """
        result = urlparse(url)
        username = result.username
        password = result.password
        database = result.path[1:]
        host = result.hostname
        port = result.port

        if username is None:
            raise ValueError(f'Invalid database URL user: {url}')
        if password is None:
            raise ValueError(f'Invalid database URL password: {url}')
        if database is None:
            raise ValueError(f'Invalid database URL dbname: {url}')
        if host is None:
            raise ValueError(f'Invalid database URL host: {url}')
        if port is None:
            raise ValueError(f'Invalid database URL port: {url}')

        return {'dbname': database, 'user': username, 'password': password, 'host': host, 'port': str(port)}

    def _create_connection(self, dbname: str, username: str, password: str, host: str, port: str) -> Any:
        """Create a direct connection to PostgreSQL database.

        Args:
            dbname: Database name.
            username: Username.
            password: Password.
            host: Host address.
            port: Port number.

        Returns:
            PostgreSQL connection object.

        Raises:
            ConnectionError: If connection fails.
        """
        try:
            conn = psycopg2.connect(dbname=dbname, user=username, password=password, host=host, port=port)
            return conn
        except psycopg2.OperationalError as e:
            raise ConnectionError(f'Error connecting to PostgreSQL database: {e}')

    def _create_connection_from_url(self, db_url: str) -> Any:
        """Create a connection to PostgreSQL database from URL.

        Args:
            db_url: Database connection URL.

        Returns:
            PostgreSQL connection object.

        Raises:
            ConnectionError: If connection fails.
        """
        params = self.get_url_connection_params(db_url)
        return self._create_connection(
            params['dbname'], params['user'], params['password'], params['host'], params['port']
        )
