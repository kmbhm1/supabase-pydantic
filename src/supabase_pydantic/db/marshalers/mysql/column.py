"""MySQL column marshaler implementation."""

import logging

from supabase_pydantic.db.database_type import DatabaseType
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

# Get Logger
logger = logging.getLogger(__name__)


class MySQLColumnMarshaler(BaseColumnMarshaler):
    """MySQL column marshaler implementation."""

    def standardize_column_name(self, column_name: str, disable_model_prefix_protection: bool = False) -> str:
        """Standardize column names across database types."""
        result = std_column_name(column_name, disable_model_prefix_protection)
        return str(result) if result is not None else ''

    def get_alias(self, column_name: str) -> str:
        """Get alias for a column name."""
        result = get_col_alias(column_name)
        return str(result) if result is not None else ''

    def process_column_type(self, db_type: str, type_info: str, extra_info: dict | None = None) -> str:
        """Process database-specific column type into standard Python type."""
        # Use the common process_udt_field function with MySQL database type
        result = process_udt_field(type_info, db_type, db_type=DatabaseType.MYSQL)
        return str(result) if result is not None else ''

    def process_array_type(self, element_type: str) -> str:
        """Process array types for the database.

        MySQL doesn't natively support array types like PostgreSQL, but we implement
        this method for compatibility with the base class.
        """
        return f'list[{element_type}]'
