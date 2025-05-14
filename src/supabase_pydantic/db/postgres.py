"""PostgreSQL adapter for database interactions."""

import logging
import re
from typing import Any

import psycopg2

from src.supabase_pydantic.db.constants import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING,
    GET_CONSTRAINTS,
    GET_ENUM_TYPES,
    GET_TABLE_COLUMN_DETAILS,
    POSTGRES_SQL_CONN_REGEX,
    SCHEMAS_QUERY,
)
from src.supabase_pydantic.db.exceptions import ConnectionError
from src.supabase_pydantic.db.marshaler import construct_table_info
from src.supabase_pydantic.db.models import TableInfo


class PostgresAdapter:
    """Adapter for PostgreSQL database connections and operations."""

    def __init__(self):
        """Initialize the PostgresAdapter."""
        self.conn = None

    def _create_connection_from_db_url(self, db_url: str) -> Any:
        """Create a connection from a database URL.

        Args:
            db_url: The database URL in the format postgresql://user:pass@host:port/dbname

        Returns:
            A psycopg2 connection object.
        """
        if not re.match(POSTGRES_SQL_CONN_REGEX, db_url):
            raise ConnectionError(f'Invalid PostgreSQL connection URL: {db_url}')

        try:
            return psycopg2.connect(db_url)
        except Exception as e:
            raise ConnectionError(f'Failed to connect to PostgreSQL: {str(e)}')

    def _create_connection_from_config(self, host: str, port: str, dbname: str, user: str, password: str) -> Any:
        """Create a connection from individual configuration parameters.

        Args:
            host: The database host.
            port: The database port.
            dbname: The database name.
            user: The database user.
            password: The database password.

        Returns:
            A psycopg2 connection object.
        """
        try:
            return psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        except Exception as e:
            raise ConnectionError(f'Failed to connect to PostgreSQL: {str(e)}')

    def query_database(self, conn: Any, query: str, params: tuple = ()) -> list[tuple]:
        """Execute a query on the database and return the results.

        Args:
            conn: The database connection.
            query: The SQL query to execute.
            params: The parameters to pass to the query.

        Returns:
            List of tuples containing the query results.
        """
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            conn.rollback()
            logging.error(f'Error executing query: {query} with params {params}')
            logging.error(str(e))
            raise
        finally:
            cursor.close()

    def get_schemas(self, conn: Any) -> list[str]:
        """Get the available schemas from the database.

        Args:
            conn: The database connection.

        Returns:
            List of schema names.
        """
        rows = self.query_database(conn, SCHEMAS_QUERY)
        return [row[0] for row in rows]

    def get_table_info(self, conn: Any, schema: str = 'public') -> list[TableInfo]:
        """Get the table information from the database.

        Args:
            conn: The database connection.
            schema: The schema name to get tables from.

        Returns:
            List of TableInfo objects.
        """
        column_details = self.query_database(conn, GET_ALL_PUBLIC_TABLES_AND_COLUMNS, (schema,))
        fk_details = self.query_database(conn, GET_TABLE_COLUMN_DETAILS, (schema,))
        constraints = self.query_database(conn, GET_CONSTRAINTS, (schema,))
        enum_types = self.query_database(conn, GET_ENUM_TYPES)
        enum_type_mapping = self.query_database(conn, GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING)

        return construct_table_info(
            column_details=column_details,
            fk_details=fk_details,
            constraints=constraints,
            enum_types=enum_types,
            enum_type_mapping=enum_type_mapping,
            schema=schema,
        )
