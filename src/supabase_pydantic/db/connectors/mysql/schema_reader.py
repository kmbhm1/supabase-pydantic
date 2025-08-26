"""MySQL schema reader for retrieving database schema information."""

import logging
import re
from typing import Any, cast

from mysql.connector.connection import MySQLConnection

from supabase_pydantic.db.abstract.base_schema_reader import BaseSchemaReader
from supabase_pydantic.db.connectors.mysql.connector import MySQLConnector
from supabase_pydantic.db.drivers.mysql.queries import (
    COLUMNS_QUERY,
    CONSTRAINTS_QUERY,
    ENUMS_QUERY,
    FOREIGN_KEYS_QUERY,
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    SCHEMAS_QUERY,
    TABLES_QUERY,
    USER_DEFINED_TYPES_QUERY,
)

# Get Logger
logger = logging.getLogger(__name__)


class MySQLSchemaReader(BaseSchemaReader):
    """MySQL schema reader for retrieving database schema information."""

    def __init__(self, connector: MySQLConnector):
        """Initialize the MySQL schema reader.

        Args:
            connector: MySQL database connector
        """
        self.connector = connector

    def execute_query(
        self, connection: MySQLConnection, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a query on the MySQL database and return the results.

        Args:
            connection: MySQL connection
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query results as a list of dictionaries
        """
        cursor = connection.cursor(dictionary=True)
        try:
            # MySQL Connector uses different parameter substitution than what's in our queries
            # Convert dictionary parameters to tuple format for proper MySQL parameter binding
            if params:
                # Replace named parameters with positional parameters
                # MySQL uses %s for parameter placeholders regardless of type
                param_values = tuple(params.values())
                param_names = list(params.keys())

                # Log the actual query being executed with values for debugging
                query_log = query
                for i, _ in enumerate(param_names):
                    param_value = param_values[i]
                    safe_value = repr(param_value) if param_value is not None else 'NULL'
                    query_log = query_log.replace('%s', f"'{safe_value}'", 1)

                logger.debug('Executing MySQL query with parameters:')
                logger.debug(f'Parameter dict: {params}')
                logger.debug(f'Parameter values: {param_values}')
                logger.debug(f'Final query (simulated): {query_log}')

                cursor.execute(query, param_values)
            else:
                logger.debug(f'Executing MySQL query without parameters: {query}')
                cursor.execute(query)

            results = cursor.fetchall()
            return cast(list[dict[str, Any]], results)
        except Exception as e:
            logger.error(f'MySQL query execution failed: {e}')
            logger.error(f'Failed query: {query}')
            if params:
                logger.error(f'Failed query parameters: {params}')
            raise
        finally:
            cursor.close()

    def parse_mysql_enum_values(self, enum_values_string: str) -> list[str]:
        """Parse MySQL enum values string into a list.

        MySQL enum values come as a comma-separated string with quotes like:
        'value1','value2','value3'

        MySQL supports two ways of escaping single quotes in enum values:
        1. Using a backslash: 'value\'2'
        2. Using doubled quotes: 'value''3'

        Args:
            enum_values_string: String of enum values from MySQL

        Returns:
            List of enum values
        """  # noqa: D301
        if not enum_values_string:
            return []

        # First, temporarily replace doubled quotes with a unique marker
        # This prevents them from being treated as closing quotes
        marker = '###QUOTED_QUOTE###'
        processed_string = enum_values_string.replace("''", marker)

        # Use the existing regex to find quoted values
        matches = re.findall(r"'((?:[^'\\]|\\.)*)'", processed_string)

        # Process the matches to restore the escaped quotes
        values = []
        for value in matches:
            # Handle backslash escaping
            processed = value.replace("\\'", "'")
            # Restore the doubled quotes to single quotes
            processed = processed.replace(marker, "'")
            values.append(processed)

        return values

    def get_schemas(self, connection: MySQLConnection) -> list[str]:
        """Get all schemas in the database.

        Args:
            connection: MySQL connection

        Returns:
            List of schema names
        """
        try:
            logger.debug('Executing MySQL schema query: %s', SCHEMAS_QUERY)
            result = self.execute_query(connection, SCHEMAS_QUERY)
            schemas = [row['SCHEMA_NAME'] for row in result]
            logger.info(f'Found schemas: {schemas}')
            return schemas
        except Exception as e:
            logger.error(f'Error retrieving schemas: {e}')
            return []

    def get_tables(self, connection: MySQLConnection, schema: str) -> list[dict[str, Any]]:
        """Get all tables in the schema.

        Args:
            connection: MySQL connection
            schema: Schema name

        Returns:
            List of table information dictionaries
        """
        try:
            params = {'schema': schema}
            logger.debug(f"Executing MySQL tables query for schema '{schema}': {TABLES_QUERY}")
            result = self.execute_query(connection, TABLES_QUERY, params)
            table_names = [row.get('TABLE_NAME', 'unknown') for row in result]
            logger.info(f'Found {len(result)} tables in schema {schema}: {table_names}')
            return result
        except Exception as e:
            logger.error(f'Error retrieving tables for schema {schema}: {e}')
            return []

    def get_columns(
        self, connection: MySQLConnection, schema: str, table_name: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all columns for all tables in the schema or for a specific table.

        Args:
            connection: MySQL connection
            schema: Schema name
            table_name: Optional table name to filter columns

        Returns:
            List of column information dictionaries
        """
        try:
            # Use the comprehensive query that gets all tables and columns at once
            if table_name is None:
                params = {'schema': schema}
                result = self.execute_query(connection, GET_ALL_PUBLIC_TABLES_AND_COLUMNS, params)
                logger.info(f'Found {len(result)} columns across all tables in schema {schema}')
            else:
                # For specific table, continue using the existing query
                params = {'schema': schema, 'table_name': table_name}
                result = self.execute_query(connection, COLUMNS_QUERY, params)
                logger.info(f'Found {len(result)} columns for table {table_name} in schema {schema}')
            return result
        except Exception as e:
            logger.error(f'Error retrieving columns for schema {schema}: {e}')
            return []

    def get_constraints(self, connection: MySQLConnection, schema: str) -> list[dict[str, Any]]:
        """Get all constraints for all tables in the schema.

        Args:
            connection: MySQL connection
            schema: Schema name

        Returns:
            List of constraint information dictionaries
        """
        try:
            params = {'schema': schema}
            result = self.execute_query(connection, CONSTRAINTS_QUERY, params)
            logger.info(f'Found {len(result)} constraints in schema {schema}')
            return result
        except Exception as e:
            logger.error(f'Error retrieving constraints for schema {schema}: {e}')
            return []

    def get_foreign_keys(self, connection: MySQLConnection, schema: str) -> list[dict[str, Any]]:
        """Get all foreign keys for all tables in the schema.

        Args:
            connection: MySQL connection
            schema: Schema name

        Returns:
            List of foreign key information dictionaries
        """
        try:
            params = {'schema': schema}
            result = self.execute_query(connection, FOREIGN_KEYS_QUERY, params)
            logger.info(f'Found {len(result)} foreign keys in schema {schema}')
            return result
        except Exception as e:
            logger.error(f'Error retrieving foreign keys for schema {schema}: {e}')
            return []

    def get_user_defined_types(self, connection: MySQLConnection, schema: str) -> list[dict[str, Any]]:
        """Get all user-defined types in the schema.

        Args:
            connection: MySQL connection
            schema: Schema name

        Returns:
            List of user-defined type information dictionaries
        """
        try:
            # MySQL doesn't have user-defined types in the same way as PostgreSQL
            # Here we're primarily looking for ENUM types
            params = {'schema': schema}
            result = self.execute_query(connection, ENUMS_QUERY, params)

            # Process the enum values to convert from string to array format
            for row in result:
                if 'enum_values' in row and row['enum_values']:
                    row['enum_values'] = self.parse_mysql_enum_values(row['enum_values'])

            logger.info(f'Found {len(result)} enum types in schema {schema}')
            return result
        except Exception as e:
            logger.error(f'Error retrieving user-defined types for schema {schema}: {e}')
            return []

    def get_type_mappings(self, connection: MySQLConnection, schema: str) -> list[dict[str, Any]]:
        """Get all user-defined type mappings in the schema.

        Args:
            connection: MySQL connection
            schema: Schema name

        Returns:
            List of user-defined type mapping dictionaries
        """
        try:
            params = {'schema': schema}
            result = self.execute_query(connection, USER_DEFINED_TYPES_QUERY, params)
            logger.info(f'Found {len(result)} type mappings in schema {schema}')
            return result
        except Exception as e:
            logger.error(f'Error retrieving type mappings for schema {schema}: {e}')
            return []
