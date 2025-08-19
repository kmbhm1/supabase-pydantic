"""MySQL database connector implementation."""

import logging
from typing import Any, Literal
from urllib.parse import urlparse

import pymysql
from pymysql.cursors import DictCursor

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.exceptions import ConnectionError

# Get Logger
logger = logging.getLogger(__name__)


def create_mysql_connection(dbname: str, username: str, password: str, host: str, port: str) -> Any:
    """Create a connection to the MySQL database."""
    try:
        conn = pymysql.connect(
            database=dbname, user=username, password=password, host=host, port=int(port), cursorclass=DictCursor
        )
        return conn
    except pymysql.Error as e:
        raise ConnectionError(f'Error connecting to MySQL database: {e}')


def create_mysql_connection_from_url(db_url: str) -> Any:
    """Create a connection to the MySQL database from a URL."""
    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]  # Remove leading '/'
    host = result.hostname
    if result.port is None:
        port = '3306'  # Default MySQL port
    else:
        port = str(result.port)

    # Validate connection parameters
    if not username:
        raise ConnectionError(f'Invalid database URL user: {db_url}')
    if not password:
        raise ConnectionError(f'Invalid database URL password: {db_url}')
    if not database:
        raise ConnectionError(f'Invalid database URL dbname: {db_url}')
    if not host:
        raise ConnectionError(f'Invalid database URL host: {db_url}')

    logger.info(f'Connecting to MySQL database: {database} on host: {host} with user: {username} and port: {port}')
    return create_mysql_connection(database, username, password, host, port)


def check_mysql_connection(conn: Any) -> bool:
    """Check if the MySQL connection is open."""
    try:
        conn.ping(reconnect=False)
        logger.info('MySQL connection is open.')
        return True
    except pymysql.Error:
        logger.info('MySQL connection is closed.')
        return False


class MySQLConnector(BaseDBConnector):
    """MySQL database connector implementation."""

    def __init__(self, conn_type: DatabaseConnectionType, **kwargs: Any):
        """Initialize the MySQL connector.

        Args:
            conn_type: Type of connection (LOCAL, DB_URL)
            **kwargs: Connection parameters
        """
        self.conn_type = conn_type
        self.kwargs = kwargs
        self.conn = None

    def connect(self) -> Any:
        """Connect to the MySQL database."""
        if self.conn_type == DatabaseConnectionType.DB_URL:
            self.conn = create_mysql_connection_from_url(self.kwargs['DB_URL'])
        elif self.conn_type == DatabaseConnectionType.LOCAL:
            try:
                self.conn = create_mysql_connection(
                    self.kwargs['DB_NAME'],
                    self.kwargs['DB_USER'],
                    self.kwargs['DB_PASS'],
                    self.kwargs['DB_HOST'],
                    self.kwargs['DB_PORT'] if 'DB_PORT' in self.kwargs else '3306',
                )
            except KeyError:
                raise ValueError('Invalid MySQL connection parameters.')
        else:
            raise ValueError(f'Invalid connection type: {self.conn_type}')

        return self.conn

    def disconnect(self) -> None:
        """Disconnect from the MySQL database."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info('MySQL connection closed.')

    def check_connection(self) -> bool:
        """Check if the connection to the MySQL database is open."""
        if not self.conn:
            logger.info('No MySQL connection established.')
            return False
        return check_mysql_connection(self.conn)

    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Execute a query on the MySQL database.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query results
        """
        if not self.conn:
            raise ConnectionError('No MySQL connection established.')

        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        finally:
            cursor.close()

    def __enter__(self) -> Any:
        """Enter context manager."""
        return self.connect()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        """Exit context manager."""
        self.disconnect()
        return False
