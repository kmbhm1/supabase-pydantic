"""PostgreSQL schema reader implementation."""

import logging
from typing import Any

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.abstract.base_schema_reader import BaseSchemaReader
from supabase_pydantic.db.drivers.postgres.queries import (
    GET_ALL_PUBLIC_TABLES_AND_COLUMNS,
    GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING,
    GET_CONSTRAINTS,
    GET_ENUM_TYPES,
    GET_TABLE_COLUMN_DETAILS,
    SCHEMAS_QUERY,
    TABLES_QUERY,
)

# Get Logger
logger = logging.getLogger(__name__)


class PostgresSchemaReader(BaseSchemaReader):
    """PostgreSQL schema reader implementation."""

    def __init__(self, connector: BaseDBConnector):
        """Initialize with a PostgreSQL connector.

        Args:
            connector: PostgreSQL connector instance.
        """
        logger.info('PostgresSchemaReader initialized')
        super().__init__(connector)

    def get_schemas(self, conn: Any) -> list[str]:
        """Get all schemas in the PostgreSQL database.

        Args:
            conn: PostgreSQL connection object.

        Returns:
            List of schema names.
        """
        schemas_result = self.connector.execute_query(conn, SCHEMAS_QUERY)
        return [schema[0] for schema in schemas_result]

    def get_tables(self, conn: Any, schema: str) -> list[tuple]:
        """Get all tables in the specified schema.

        Args:
            conn: PostgreSQL connection object.
            schema: Schema name.

        Returns:
            List of table information as tuples.
        """
        result = self.connector.execute_query(conn, TABLES_QUERY, (schema,))
        return result if isinstance(result, list) else []

    def get_columns(self, conn: Any, schema: str) -> list[tuple[Any, ...]]:
        """Get all columns in the specified schema.

        Args:
            conn: PostgreSQL connection object.
            schema: Schema name.

        Returns:
            List of column information as tuples.
        """
        result = self.connector.execute_query(conn, GET_ALL_PUBLIC_TABLES_AND_COLUMNS, (schema,))
        return result if isinstance(result, list) else []

    def get_foreign_keys(self, conn: Any, schema: str) -> list[tuple[Any, ...]]:
        """Get all foreign keys in the specified schema.

        Args:
            conn: PostgreSQL connection object.
            schema: Schema name.

        Returns:
            List of foreign key information as tuples.
        """
        result = self.connector.execute_query(conn, GET_TABLE_COLUMN_DETAILS, (schema,))
        return result if isinstance(result, list) else []

    def get_constraints(self, conn: Any, schema: str) -> list[tuple[Any, ...]]:
        """Get all constraints in the specified schema.

        Args:
            conn: PostgreSQL connection object.
            schema: Schema name.

        Returns:
            List of constraint information as tuples.
        """
        result = self.connector.execute_query(conn, GET_CONSTRAINTS, (schema,))
        return result if isinstance(result, list) else []

    def get_user_defined_types(self, conn: Any, schema: str) -> list[tuple[Any, ...]]:
        """Get all user-defined types in the specified schema.

        Args:
            conn: PostgreSQL connection object.
            schema: Schema name.

        Returns:
            List of user-defined type information as tuples.
        """
        result = self.connector.execute_query(conn, GET_ENUM_TYPES, (schema,))
        return result if isinstance(result, list) else []

    def get_type_mappings(self, conn: Any, schema: str) -> list[tuple[Any, ...]]:
        """Get type mapping information for the specified schema.

        Args:
            conn: PostgreSQL connection object.
            schema: Schema name.

        Returns:
            List of type mapping information as tuples.
        """
        result = self.connector.execute_query(conn, GET_COLUMN_TO_USER_DEFINED_TYPE_MAPPING, (schema,))
        return result if isinstance(result, list) else []
