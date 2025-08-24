"""Database-agnostic table construction module."""

import logging
from typing import Any

from supabase_pydantic.db.abstract.base_connector import BaseDBConnector
from supabase_pydantic.db.abstract.base_schema_reader import BaseSchemaReader
from supabase_pydantic.db.constants import DatabaseConnectionType
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.factory import DatabaseFactory
from supabase_pydantic.db.marshalers.abstract.base_schema_marshaler import BaseSchemaMarshaler
from supabase_pydantic.db.models import TableInfo
from supabase_pydantic.db.registrations import register_database_components

# Get Logger
logger = logging.getLogger(__name__)


class DatabaseBuilder:
    """Database-agnostic builder for table information."""

    def __init__(
        self,
        db_type: DatabaseType,
        conn_type: DatabaseConnectionType,
        connection_params: Any = None,
        **kwargs: Any,
    ):
        """Initialize the database builder.

        Args:
            db_type: Type of database (PostgreSQL, MySQL, etc.)
            conn_type: Type of connection (LOCAL, DB_URL, etc.)
            connection_params: Connection parameters as Pydantic model or dict
            **kwargs: Additional connection parameters
        """
        self.db_type = db_type
        self.conn_type = conn_type

        # Register database components before using the factory
        register_database_components()

        # Create components using factory
        factory = DatabaseFactory()
        self.connector: BaseDBConnector = factory.create_connector(
            db_type, connection_params=connection_params, **kwargs
        )
        self.schema_reader: BaseSchemaReader = factory.create_schema_reader(db_type, connector=self.connector)
        self.marshaler: BaseSchemaMarshaler = factory.create_marshalers(db_type)

    def build_tables(
        self,
        schemas: tuple[str, ...] = ('public',),
        disable_model_prefix_protection: bool = False,
    ) -> dict[str, list[TableInfo]]:
        """Build table information from database.

        Args:
            schemas: Tuple of schema names to process.
            disable_model_prefix_protection: If True, disable model_ prefix protection.

        Returns:
            Dictionary of schema names to lists of TableInfo objects.
        """
        all_tables_info: dict[str, list[TableInfo]] = {}

        # Connect to database
        with self.connector as connection:
            if not self.connector.check_connection(connection):
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    raise ConnectionError('Failed to establish database connection')
                else:
                    logger.error('Failed to establish database connection')
                    return all_tables_info

            # Discover all schemas
            schema_names = self.schema_reader.get_schemas(connection)
            for schema_name in schema_names:
                # Skip schemas that are not in the list of schemas from user
                # If the list of schemas is '*', include all schemas
                if schema_name not in schemas and schemas != ('*',):
                    continue

                # Fetch schema information
                logger.info(f'Processing schema: {schema_name}')

                # Get raw data
                table_data = self.schema_reader.get_tables(connection, schema_name)
                column_data = self.schema_reader.get_columns(connection, schema_name)
                constraint_data = self.schema_reader.get_constraints(connection, schema_name)
                fk_data = self.schema_reader.get_foreign_keys(connection, schema_name)
                user_defined_types = self.schema_reader.get_user_defined_types(connection, schema_name)
                type_mappings = self.schema_reader.get_type_mappings(connection, schema_name)

                # Construct table info using schema marshaler
                all_tables_info[schema_name] = self.marshaler.construct_table_info(
                    table_data=table_data,
                    column_data=column_data,
                    fk_data=fk_data,
                    constraint_data=constraint_data,
                    type_data=user_defined_types,
                    type_mapping_data=type_mappings,
                    schema=schema_name,
                    disable_model_prefix_protection=disable_model_prefix_protection,
                )

        return all_tables_info


def construct_tables(
    conn_type: DatabaseConnectionType,
    db_type: DatabaseType = DatabaseType.POSTGRES,
    schemas: tuple[str, ...] = ('public',),
    disable_model_prefix_protection: bool = False,
    connection_params: Any = None,
    **kwargs: Any,
) -> dict[str, list[TableInfo]]:
    """Database-agnostic function to construct table information.

    Args:
        conn_type: Type of connection (LOCAL, DB_URL, etc.)
        db_type: Type of database (PostgreSQL, MySQL, etc.)
        schemas: Tuple of schema names to process.
        disable_model_prefix_protection: If True, disable model_ prefix protection.
        connection_params: Connection parameters as a Pydantic model or dictionary.
        **kwargs: Additional connection parameters as keyword arguments.

    Returns:
        Dictionary of schema names to lists of TableInfo objects.
    """
    # Combine connection_params with any additional kwargs
    if connection_params is None:
        builder = DatabaseBuilder(db_type, conn_type, **kwargs)
    else:
        builder = DatabaseBuilder(db_type, conn_type, connection_params=connection_params, **kwargs)

    return builder.build_tables(
        schemas=schemas,
        disable_model_prefix_protection=disable_model_prefix_protection,
    )
