import re
from typing import Any

from supabase_pydantic.db.marshalers.column import standardize_column_name
from supabase_pydantic.db.models import ConstraintInfo


def parse_constraint_definition_for_fk(constraint_definition: str) -> tuple[str, str, str] | None:
    """Parse the foreign key definition from the constraint."""
    match = re.match(r'FOREIGN KEY \(([^)]+)\) REFERENCES (\S+)\(([^)]+)\)', constraint_definition)
    if match:
        column_name = match.group(1)
        foreign_table_name = match.group(2)
        foreign_column_name = match.group(3)

        return column_name, foreign_table_name, foreign_column_name
    return None


def add_constraints_to_table_details(tables: dict, schema: str, constraints: list) -> None:
    """Add constraints to the table details."""
    for row in constraints:
        (constraint_name, table_name, columns, constraint_type, constraint_definition) = row

        # Remove schema from the beginning of table_name if present
        if table_name.startswith(f'{schema}.'):
            table_name = table_name[len(schema) + 1 :]  # Remove schema and the dot  # noqa: E203
        table_name = table_name.lstrip('.')  # Remove any leading dots
        table_key = (schema, table_name)

        # Create the constraint and add it to the table
        if table_key in tables:
            constraint = ConstraintInfo(
                constraint_name=constraint_name,
                columns=[standardize_column_name(c) or str(c) for c in columns],
                raw_constraint_type=constraint_type,
                constraint_definition=constraint_definition,
            )
            tables[table_key].add_constraint(constraint)


def get_unique_columns_from_constraints(constraint: ConstraintInfo) -> list[str | Any]:
    """Get unique columns from constraints."""
    unique_columns = []
    if constraint.constraint_type() == 'UNIQUE':
        match = re.match(r'UNIQUE \(([^)]+)\)', constraint.constraint_definition)
        if match:
            columns = match.group(1).split(',')
            unique_columns = [c.strip() for c in columns]
    return unique_columns


def update_column_constraint_definitions(tables: dict) -> None:
    """Update columns with their CHECK constraint definitions."""
    for table in tables.values():
        if table.columns is None or len(table.columns) == 0:
            continue
        if table.constraints is None or len(table.constraints) == 0:
            continue

        # iterate through columns and constraints
        for column in table.columns:
            for constraint in table.constraints:
                # Only process CHECK constraints that affect this column
                if constraint.constraint_type() == 'CHECK' and len(constraint.columns) == 1:
                    if column.name == constraint.columns[0]:
                        column.constraint_definition = constraint.constraint_definition


def update_columns_with_constraints(tables: dict) -> None:
    """Update columns with constraints."""
    for table in tables.values():
        if table.columns is None or len(table.columns) == 0:
            continue
        if table.constraints is None or len(table.constraints) == 0:
            continue

        # iterate through columns and constraints
        for column in table.columns:
            for constraint in table.constraints:
                for col in constraint.columns:
                    if column.name == col:
                        if constraint.constraint_type() == 'PRIMARY KEY':
                            column.primary = True
                        if constraint.constraint_type() == 'UNIQUE':
                            column.is_unique = True
                            column.unique_partners = get_unique_columns_from_constraints(constraint)
                        if constraint.constraint_type() == 'FOREIGN KEY':
                            column.is_foreign_key = True
                        if constraint.constraint_type() == 'CHECK' and len(constraint.columns) == 1:
                            column.constraint_definition = constraint.constraint_definition
