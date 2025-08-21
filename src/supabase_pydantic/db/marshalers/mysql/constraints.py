"""MySQL constraint marshaler implementation."""

import logging
import re
from typing import Any, cast

from supabase_pydantic.db.drivers.mysql.constants import MYSQL_CONSTRAINT_TYPE_MAP
from supabase_pydantic.db.marshalers.abstract.base_constraint_marshaler import BaseConstraintMarshaler
from supabase_pydantic.db.marshalers.constraints import (
    add_constraints_to_table_details as add_constraints,
)
from supabase_pydantic.db.marshalers.constraints import (
    parse_constraint_definition_for_fk,
)
from supabase_pydantic.db.models import ConstraintInfo, TableInfo

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
            return (source_column.strip('`'), target_table.strip('`'), target_column.strip('`'))

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

    def marshal(
        self, data: list[dict[str, Any]], schema: str, **kwargs: Any
    ) -> dict[tuple[str, str], list[ConstraintInfo]]:
        """Marshal constraint data into ConstraintInfo objects.

        Args:
            data: Raw constraint data from the database
            schema: Schema name
            **kwargs: Additional arguments

        Returns:
            Dictionary of table names to lists of ConstraintInfo objects
        """
        if not data:
            logger.warning(f'No constraint data to marshal for schema {schema}')
            return {}

        # Group constraints by table
        table_constraints: dict[tuple[str, str], list[ConstraintInfo]] = {}
        processed_constraints: set[str] = set()  # Track processed constraints to avoid duplicates

        for constraint in data:
            table_name = constraint.get('table_name', '')
            constraint_name = constraint.get('constraint_name', '')

            # Skip if missing essential data
            if not table_name or not constraint_name:
                logger.warning(f'Constraint data missing table_name or constraint_name: {constraint}')
                continue

            # Skip if already processed this constraint for this table
            constraint_key = f'{table_name}:{constraint_name}'
            if constraint_key in processed_constraints:
                continue
            processed_constraints.add(constraint_key)

            # Get constraint type with fallback
            constraint_type = constraint.get('constraint_type', '')
            constraint_type_mapped = MYSQL_CONSTRAINT_TYPE_MAP.get(constraint_type, 'OTHER')

            # Handle column lists from GROUP_CONCAT in MySQL query
            column_list = constraint.get('column_list', '')
            if column_list:
                columns = column_list.split(',')
            else:
                columns = [constraint.get('column_name', '')]
                columns = [col for col in columns if col]  # Remove empty strings

            # Create constraint info
            constraint_info = ConstraintInfo(
                name=constraint_name,
                columns=columns,
                table=table_name,
                schema=schema,
                constraint_type=constraint_type_mapped,
            )

            # Add to table constraints
            table_key = (schema, table_name)
            if table_key not in table_constraints:
                table_constraints[table_key] = []
            table_constraints[table_key].append(constraint_info)

        return table_constraints
