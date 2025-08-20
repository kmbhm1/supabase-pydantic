"""MySQL column marshaler implementation."""

import logging
from typing import Any

from supabase_pydantic.db.drivers.mysql.constants import MYSQL_USER_DEFINED_TYPE_MAP
from supabase_pydantic.db.marshalers.abstract.base_column_marshaler import BaseColumnMarshaler
from supabase_pydantic.db.marshalers.column import (
    get_alias as get_col_alias,
)
from supabase_pydantic.db.marshalers.column import (
    process_udt_field,
)
from supabase_pydantic.db.marshalers.column import (
    standardize_column_name as std_column_name,
)
from supabase_pydantic.db.models import ColumnInfo, SortedColumns

# Get Logger
logger = logging.getLogger(__name__)


class MySQLColumnMarshaler(BaseColumnMarshaler):
    """MySQL column marshaler implementation."""

    def standardize_column_name(self, column_name: str, disable_model_prefix_protection: bool = False) -> str:
        """Standardize column names across database types."""
        result = std_column_name(column_name, disable_model_prefix_protection)
        return result if result is not None else ''

    def get_alias(self, column_name: str) -> str:
        """Get alias for a column name."""
        result = get_col_alias(column_name)
        return result if result is not None else ''

    def process_column_type(self, db_type: str, type_info: str, extra_info: dict | None = None) -> str:
        """Process database-specific column type into standard Python type."""
        # Use the common process_udt_field function with MySQL-specific type map if needed
        result = process_udt_field(type_info, db_type, type_map=MYSQL_USER_DEFINED_TYPE_MAP)
        return result if result is not None else ''

    def process_array_type(self, element_type: str) -> str:
        """Process array types for the database.

        MySQL doesn't natively support array types like PostgreSQL, but we implement
        this method for compatibility with the base class.
        """
        return f'list[{element_type}]'

    def marshal(
        self, data: list[dict[str, Any]], schema: str, disable_model_prefix_protection: bool = False
    ) -> dict[str, SortedColumns]:
        """Marshal column data into SortedColumns objects.

        Args:
            data: Raw column data from the database
            schema: Schema name
            disable_model_prefix_protection: If True, disable model_ prefix protection

        Returns:
            Dictionary of table names to SortedColumns objects
        """
        if not data:
            logger.warning(f'No column data to marshal for schema {schema}')
            return {}

        # Group columns by table
        table_columns: dict[str, list[ColumnInfo]] = {}
        for column in data:
            table_name = column.get('table_name', '')
            if not table_name:
                logger.warning(f'Column data missing table_name: {column}')
                continue

            # Create column info
            column_info = ColumnInfo(
                name=column.get('column_name', ''),
                data_type=column.get('data_type', ''),
                is_nullable=column.get('is_nullable', 'NO').upper() == 'YES',
                default=column.get('default_value'),
                table=table_name,
                table_type=column.get('table_type', 'BASE TABLE'),
                schema=schema,
                array_element_type=column.get('array_element_type'),
                disable_model_prefix_protection=disable_model_prefix_protection,
                type_map=MYSQL_USER_DEFINED_TYPE_MAP,  # Use MySQL-specific type map
            )

            # Check for extra info like auto-increment
            extra = column.get('extra_info', '')
            column_info.is_auto_increment = 'auto_increment' in extra.lower()

            # Add to table columns
            if table_name not in table_columns:
                table_columns[table_name] = []
            table_columns[table_name].append(column_info)

        # Sort columns and create SortedColumns objects
        sorted_columns: dict[str, SortedColumns] = {}
        for table_name, columns in table_columns.items():
            sorted_columns[table_name] = SortedColumns(columns=columns)

        return sorted_columns
