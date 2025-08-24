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


class PostgresColumnMarshaler(BaseColumnMarshaler):
    """PostgreSQL-specific implementation of column marshaling."""

    def standardize_column_name(self, column_name: str, disable_model_prefix_protection: bool = False) -> str:
        """Standardize column names across database types."""
        result = std_column_name(column_name, disable_model_prefix_protection)
        return str(result) if result is not None else ''

    def get_alias(self, column_name: str) -> str:
        """Get alias for a column name."""
        result = get_col_alias(column_name)
        return str(result) if result is not None else ''

    def process_column_type(self, db_type: str, type_info: str, enum_types: list[str] | None = None) -> str:
        """Process database-specific column type into standard Python type."""
        result = process_udt_field(type_info, db_type, known_enum_types=enum_types)
        if result is None:
            return ''
        # Make sure we check for None again and return empty string
        # This can happen if the underlying function changes behavior
        return '' if result is None else str(result)

    def process_array_type(self, element_type: str) -> str:
        """Process array types for the database."""
        return f'list[{element_type}]'
