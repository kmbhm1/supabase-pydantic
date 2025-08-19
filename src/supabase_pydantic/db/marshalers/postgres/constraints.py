import re

from supabase_pydantic.db.marshalers.abstract.base_constraint_marshaler import BaseConstraintMarshaler
from supabase_pydantic.db.marshalers.constraints import (
    add_constraints_to_table_details as add_constraints,
)
from supabase_pydantic.db.marshalers.constraints import (
    parse_constraint_definition_for_fk,
)
from supabase_pydantic.db.models import TableInfo


class PostgresConstraintMarshaler(BaseConstraintMarshaler):
    """PostgreSQL implementation of constraint marshaling."""

    def parse_foreign_key(self, constraint_def: str) -> tuple[str, str, str] | None:
        """Parse foreign key definition from database-specific syntax."""
        result = parse_constraint_definition_for_fk(constraint_def)
        return result if result else None

    def parse_unique_constraint(self, constraint_def: str) -> list[str]:
        """Parse unique constraint from database-specific syntax."""
        match = re.match(r'UNIQUE \(([^)]+)\)', constraint_def)
        if match:
            columns = match.group(1).split(',')
            return [c.strip() for c in columns]
        return []

    def parse_check_constraint(self, constraint_def: str) -> str:
        """Parse check constraint from database-specific syntax."""
        # For PostgreSQL, just return the constraint definition as is
        return constraint_def

    def add_constraints_to_table_details(
        self, tables: dict[tuple[str, str], TableInfo], constraint_data: list[tuple], schema: str
    ) -> None:
        """Add constraint information to table details."""
        add_constraints(tables, schema, constraint_data)
