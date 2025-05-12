"""PostgreSQL adapter implementation for database connections and schema introspection."""

import logging
import re
from typing import Any
from urllib.parse import urlparse

import psycopg2

from src.supabase_pydantic.utils.constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING,
    GET_CONSTRAINTS,
    GET_ENUM_TYPES,
    GET_TABLE_COLUMN_DETAILS,
    POSTGRES_SQL_CONN_REGEX,
    PYDANTIC_TYPE_MAP,
    SCHEMAS_QUERY,
)
from src.supabase_pydantic.utils.dataclasses import TableInfo
from src.supabase_pydantic.utils.marshalers import construct_table_info

from .base import DatabaseAdapter


class PostgresAdapter(DatabaseAdapter):
    """PostgreSQL database adapter implementation."""

    def __init__(self, **connection_params: Any) -> None:
        """Initialize the PostgreSQL adapter with connection parameters.

        The connection parameters should include:
        - DB_NAME: Database name
        - DB_USER: Database username
        - DB_PASS: Database password
        - DB_HOST: Database host
        - DB_PORT: Database port

        Or a single DB_URL parameter with a PostgreSQL connection string.
        """
        self.connection_params = connection_params
        self.conn = None

        # Check if we have a DB_URL or individual connection parameters
        if 'DB_URL' in connection_params:
            self.connection_type = 'url'
        elif all(k in connection_params for k in ['DB_NAME', 'DB_USER', 'DB_PASS', 'DB_HOST', 'DB_PORT']):
            self.connection_type = 'params'
        else:
            raise ValueError(
                'Invalid connection parameters. Must provide either DB_URL or '
                'all of: DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT'
            )

    def connect(self) -> Any:
        """Establish a connection to the PostgreSQL database."""
        if self.connection_type == 'url':
            self.conn = self._create_connection_from_db_url(self.connection_params['DB_URL'])
        else:
            self.conn = self._create_connection(
                self.connection_params['DB_NAME'],
                self.connection_params['DB_USER'],
                self.connection_params['DB_PASS'],
                self.connection_params['DB_HOST'],
                self.connection_params['DB_PORT'],
            )
        return self.conn

    def close(self) -> None:
        """Close the PostgreSQL database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logging.info('PostgreSQL connection is closed.')

    def check_connection(self) -> bool:
        """Check if the connection to the PostgreSQL database is active."""
        if self.conn is None:
            logging.info('No PostgreSQL connection exists.')
            return False

        if self.conn.closed:
            logging.info('PostgreSQL connection is closed.')
            return False
        else:
            logging.info('PostgreSQL connection is open.')
            return True

    def query(self, query: str, params: tuple = ()) -> list[tuple]:
        """Execute a query against the PostgreSQL database."""
        if not self.check_connection():
            self.connect()

        cur = self.conn.cursor()
        try:
            cur.execute(query, params)
            result = cur.fetchall()
            return result
        finally:
            cur.close()

    def get_schemas(self) -> list[str]:
        """Get a list of all non-system schemas in the PostgreSQL database."""
        schemas_result = self.query(SCHEMAS_QUERY)
        return [schema[0] for schema in schemas_result]

    def get_tables(self, schema: str) -> list[tuple]:
        """Get all tables and their columns for a given schema."""
        return self.query(GET_ALL_PUBLIC_TABLES_AND_COLUMNS, (schema,))

    def get_foreign_keys(self, schema: str) -> list[tuple]:
        """Get all foreign key relationships for a given schema."""
        return self.query(GET_TABLE_COLUMN_DETAILS, (schema,))

    def get_constraints(self, schema: str) -> list[tuple]:
        """Get all constraints for a given schema."""
        return self.query(GET_CONSTRAINTS, (schema,))

    def get_user_defined_types(self, schema: str) -> list[tuple]:
        """Get all user-defined types for a given schema."""
        enum_types = self.query(GET_ENUM_TYPES, (schema,))
        enum_type_mapping = self.query(GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING, (schema,))
        return enum_types, enum_type_mapping

    def type_map(self) -> dict[str, tuple[str, str | None]]:
        """Get the mapping of PostgreSQL types to Python/Pydantic types."""
        return PYDANTIC_TYPE_MAP

    def construct_table_info(self, schema: str = 'public') -> list[TableInfo]:
        """Construct TableInfo objects from PostgreSQL schema information."""
        # Fetch the database schema information
        column_details = self.get_tables(schema)
        fk_details = self.get_foreign_keys(schema)
        constraints = self.get_constraints(schema)
        enum_types, enum_type_mapping = self.get_user_defined_types(schema)

        # Use the existing marshaler function to construct the TableInfo objects
        return construct_table_info(column_details, fk_details, constraints, enum_types, enum_type_mapping, schema)

    def _create_connection(self, dbname: str, username: str, password: str, host: str, port: str) -> Any:
        """Create a connection to the PostgreSQL database using individual parameters."""
        try:
            conn = psycopg2.connect(dbname=dbname, user=username, password=password, host=host, port=port)
            return conn
        except psycopg2.OperationalError as e:
            raise ConnectionError(f'Error connecting to PostgreSQL database: {e}')

    def _create_connection_from_db_url(self, db_url: str) -> Any:
        """Create a connection to the PostgreSQL database using a connection URL."""
        # Validate that this is a PostgreSQL URL
        if not re.match(POSTGRES_SQL_CONN_REGEX, db_url):
            raise ValueError(f'Invalid PostgreSQL database URL: {db_url}')

        result = urlparse(db_url)
        username = result.username
        password = result.password
        database = result.path[1:]
        host = result.hostname
        if result.port is None:
            raise ConnectionError(f'Invalid database URL port: {db_url}')
        port = str(result.port)

        assert username is not None, f'Invalid database URL user: {db_url}'
        assert password is not None, f'Invalid database URL pass: {db_url}'
        assert database is not None, f'Invalid database URL dbname: {db_url}'
        assert host is not None, f'Invalid database URL host: {db_url}'

        logging.info(f'Connecting to database: {database} on host: {host} with user: {username} and port: {port}')

        return self._create_connection(database, username, password, host, port)

    @classmethod
    def create_from_url(cls, db_url: str) -> 'PostgresAdapter':
        """Create a PostgreSQL adapter from a connection URL."""
        return cls(DB_URL=db_url)
