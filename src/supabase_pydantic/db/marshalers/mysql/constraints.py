"""MySQL constraint marshaler implementation."""

import logging
import re
from typing import cast

from supabase_pydantic.db.marshalers.abstract.base_constraint_marshaler import BaseConstraintMarshaler
from supabase_pydantic.db.marshalers.constraints import (
    add_constraints_to_table_details as add_constraints,
)
from supabase_pydantic.db.marshalers.constraints import (
    parse_constraint_definition_for_fk,
)
from supabase_pydantic.db.models import TableInfo

# Get Logger
logger = logging.getLogger(__name__)


class MySQLConstraintMarshaler(BaseConstraintMarshaler):
    """MySQL constraint marshaler implementation."""

    def parse_foreign_key(self, constraint_def: str) -> tuple[str, str, str] | None:
        """Parse foreign key definition from MySQL-specific syntax.

        Args:
            constraint_def: Constraint definition string.

        Returns:
            Tuple containing (source_column, target_table, target_column) or None.
        """
        # Try to use the common parser first
        result = parse_constraint_definition_for_fk(constraint_def)
        if result:
            return cast(tuple[str, str, str], result)

        # MySQL-specific parsing for FOREIGN KEY constraints
        # Example: "FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)"
        pattern = r'FOREIGN KEY\s+\(`?([^`)]+)`?\)\s+REFERENCES\s+`?([^`(]+)`?\s*\(`?([^`)]+)`?\)'
        match = re.match(pattern, constraint_def, re.IGNORECASE)
        if match:
            source_column, target_table, target_column = match.groups()
            # Strip backticks and any extra whitespace
            return (source_column.strip('`').strip(), target_table.strip('`').strip(), target_column.strip('`').strip())

        return None

    def parse_unique_constraint(self, constraint_def: str) -> list[str]:
        """Parse unique constraint from MySQL-specific syntax.

        Args:
            constraint_def: Constraint definition string.

        Returns:
            List of column names in the unique constraint.
        """
        # MySQL UNIQUE constraint format: "UNIQUE KEY `name` (`col1`, `col2`)"
        # or simply: "UNIQUE (`col1`, `col2`)"
        pattern = r'UNIQUE(?:\s+KEY\s+`?[^`]+`?)?\s*\(([^)]+)\)'
        match = re.match(pattern, constraint_def, re.IGNORECASE)
        if match:
            columns_str = match.group(1)
            # Split by comma and remove backticks
            columns = [col.strip().strip('`') for col in columns_str.split(',')]
            return columns
        return []

    def parse_check_constraint(self, constraint_def: str) -> str:
        """Parse check constraint from MySQL-specific syntax.

        Args:
            constraint_def: Constraint definition string.

        Returns:
            Parsed check constraint expression.
        """
        # MySQL CHECK constraint format: "CHECK (`col` > 0)"
        pattern = r'CHECK\s+\((.+)\)'
        match = re.match(pattern, constraint_def, re.IGNORECASE)
        if match:
            return match.group(1)
        return constraint_def

    def add_constraints_to_table_details(
        self, tables: dict[tuple[str, str], TableInfo], constraint_data: list[tuple], schema: str
    ) -> None:
        """Add constraint information to table details.

        Args:
            tables: Dictionary of table information objects.
            constraint_data: Raw constraint data from database.
            schema: Schema name.
        """
        # Use the common implementation
        add_constraints(tables, schema, constraint_data)
