"""Marshaling utilities for database schema to code model transformation.

This module contains functions for transforming database schema information
into structured Python objects that can be used for code generation.
"""

import builtins
import keyword
import logging
import pprint
import re

from src.supabase_pydantic.core.constants import PYDANTIC_TYPE_MAP, RelationType
from src.supabase_pydantic.core.models import (
    ColumnInfo,
    ConstraintInfo,
    EnumInfo,
    ForeignKeyInfo,
    RelationshipInfo,
    TableInfo,
    UserEnumType,
    UserTypeMapping,
)

pp = pprint.PrettyPrinter(indent=4)


def string_is_reserved(value: str) -> bool:
    """Check if the string is a reserved keyword or built-in name."""
    return value in dir(builtins) or value in keyword.kwlist


def column_name_is_reserved(column_name: str) -> bool:
    """Check if the column name is a reserved keyword or built-in name or starts with model_."""
    return string_is_reserved(column_name) or column_name.startswith('model_')


def column_name_reserved_exceptions(column_name: str) -> bool:
    """Check for select exceptions to the reserved column name check."""
    exceptions = ['id']
    return column_name.lower() in exceptions


def standardize_column_name(column_name: str) -> str | None:
    """Check if the column name is a reserved keyword or built-in name and replace it if necessary."""
    return (
        f'field_{column_name}'
        if column_name_is_reserved(column_name) and not column_name_reserved_exceptions(column_name)
        else column_name
    )


def get_alias(column_name: str) -> str | None:
    """Provide the original column name as an alias for Pydantic."""
    return (
        column_name
        if column_name_is_reserved(column_name) and not column_name_reserved_exceptions(column_name)
        else None
    )


def parse_constraint_definition_for_fk(constraint_definition: str) -> tuple[str, str, str] | None:
    """Parse the foreign key definition from the constraint."""
    match = re.match(r'FOREIGN KEY \(([^)]+)\) REFERENCES (\S+)\(([^)]+)\)', constraint_definition)
    if match:
        column_name = match.group(1)
        foreign_table_name = match.group(2)
        foreign_column_name = match.group(3)

        return column_name, foreign_table_name, foreign_column_name
    return None


def get_table_details_from_columns(column_details: list) -> dict[tuple[str, str], TableInfo]:
    """Get the table details from the column details."""
    tables = {}
    for row in column_details:
        (
            schema,
            table_name,
            column_name,
            default,
            is_nullable,
            data_type,
            max_length,
            table_type,
            identity_generation,
        ) = row
        table_key: tuple[str, str] = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema, table_type=table_type)
        column_info = ColumnInfo(
            name=standardize_column_name(column_name) or column_name,
            alias=get_alias(column_name),
            post_gres_datatype=data_type,
            datatype=PYDANTIC_TYPE_MAP.get(data_type, ('Any', 'from typing import Any'))[0],
            default=default,
            is_nullable=is_nullable == 'YES',
            max_length=max_length,
            is_identity=identity_generation is not None,
        )
        tables[table_key].add_column(column_info)

    return tables


def add_foreign_key_info_to_table_details(tables: dict, fk_details: list) -> None:
    """Add foreign key information to the table details.

    Skips foreign keys where either the source or target table is missing.
    This ensures that all foreign keys have valid relationship types.
    """
    for row in fk_details:
        (
            table_schema,
            table_name,
            column_name,
            foreign_table_schema,
            foreign_table_name,
            foreign_column_name,
            constraint_name,
        ) = row
        table_key = (table_schema, table_name)
        foreign_table_key = (foreign_table_schema, foreign_table_name)

        # Skip if either table is missing
        if table_key not in tables or foreign_table_key not in tables:
            continue

        # Add foreign key to source table
        standardized_column_name = standardize_column_name(column_name) or column_name
        table = tables[table_key]
        foreign_table = tables[foreign_table_key]

        foreign_key_info = ForeignKeyInfo(
            constraint_name=constraint_name,
            column_name=standardized_column_name,
            foreign_table_name=foreign_table.name,
            foreign_column_name=standardize_column_name(foreign_column_name) or foreign_column_name,
        )
        table.foreign_keys.append(foreign_key_info)


def add_constraints_to_table_details(tables: dict, schema: str, constraints: list) -> None:
    """Add constraints to the table details."""
    for row in constraints:
        constraint_name, table_name, constraint_type, constraint_definition = row
        table_key = (schema, table_name)
        if table_key not in tables:
            continue

        constraint_info = ConstraintInfo(
            name=constraint_name,
            type=constraint_type,
            definition=constraint_definition,
        )
        tables[table_key].constraints.append(constraint_info)


def add_relationships_to_table_details(tables: dict, fk_details: list) -> None:
    """Add relationships to the table details."""
    for row in fk_details:
        (
            table_schema,
            table_name,
            column_name,
            foreign_table_schema,
            foreign_table_name,
            foreign_column_name,
            constraint_name,
        ) = row
        table_key = (table_schema, table_name)
        foreign_table_key = (foreign_table_schema, foreign_table_name)

        # Skip if either table is missing
        if table_key not in tables or foreign_table_key not in tables:
            continue

        table = tables[table_key]
        foreign_table = tables[foreign_table_key]

        # Look up the column in the source table
        standardized_column_name = standardize_column_name(column_name) or column_name
        column = next((c for c in table.columns if c.name == standardized_column_name), None)
        if not column:
            continue

        # Look up the column in the target table
        standardized_foreign_column_name = standardize_column_name(foreign_column_name) or foreign_column_name
        foreign_column = next(
            (c for c in foreign_table.columns if c.name == standardized_foreign_column_name),
            None,
        )
        if not foreign_column:
            continue

        # Check if a relationship already exists
        existing_rel = next(
            (
                r
                for r in table.relationships
                if r.name == foreign_table.name and r.source_column == standardized_column_name
            ),
            None,
        )

        if existing_rel:
            # Update the existing relationship
            existing_rel.target_column = standardized_foreign_column_name
        else:
            # Add a new relationship
            relationship_info = RelationshipInfo(
                name=foreign_table.name,
                source_column=standardized_column_name,
                target_table=foreign_table.name,
                target_column=standardized_foreign_column_name,
            )
            table.relationships.append(relationship_info)

        # Add the reverse relationship
        existing_reverse_rel = next(
            (
                r
                for r in foreign_table.relationships
                if r.name == table.name and r.source_column == standardized_foreign_column_name
            ),
            None,
        )

        if existing_reverse_rel:
            # Update the existing relationship
            existing_reverse_rel.target_column = standardized_column_name
        else:
            # Add a new relationship
            reverse_relationship_info = RelationshipInfo(
                name=table.name,
                source_column=standardized_foreign_column_name,
                target_table=table.name,
                target_column=standardized_column_name,
            )
            foreign_table.relationships.append(reverse_relationship_info)


def get_enum_types(enum_types: list, schema: str) -> list[EnumInfo]:
    """Get enum types from database."""
    enum_infos = []
    for row in enum_types:
        # enum_schema, enum_name, enum_values
        enum_schema, enum_name, enum_values = row
        if enum_schema != schema:
            continue

        # Split the enum values
        values = []
        if enum_values.startswith('{') and enum_values.endswith('}'):
            # Remove the curly braces and split by comma
            values = [v.strip('"') for v in enum_values[1:-1].split(',')]

        enum_info = EnumInfo(
            name=enum_name,
            values=values,
        )
        enum_infos.append(enum_info)

    return enum_infos


def get_user_type_mappings(enum_type_mapping: list, schema: str) -> list[UserTypeMapping]:
    """Get user type mappings from database."""
    user_type_mappings = []
    for row in enum_type_mapping:
        mapping_schema, table_name, column_name, type_name, type_schema = row
        if mapping_schema != schema or type_schema != schema:
            continue

        user_type_mapping = UserTypeMapping(
            table_name=table_name,
            column_name=standardize_column_name(column_name) or column_name,
            type_name=type_name,
        )
        user_type_mappings.append(user_type_mapping)

    return user_type_mappings


def add_user_defined_types_to_tables(
    tables: dict[tuple[str, str], TableInfo],
    schema: str,
    enum_types: list,
    enum_type_mapping: list,
) -> None:
    """Get user defined types and add them to ColumnInfo."""
    # Get enum types
    enum_infos = get_enum_types(enum_types, schema)
    user_type_mappings = get_user_type_mappings(enum_type_mapping, schema)

    # Add enum types to tables
    for table_key, table in tables.items():
        table_schema, table_name = table_key

        # Check if this table has any user defined types
        for user_type_mapping in user_type_mappings:
            if user_type_mapping.table_name != table_name:
                continue

            # Find the column
            column = next(
                (c for c in table.columns if c.name == user_type_mapping.column_name),
                None,
            )
            if not column:
                continue

            # Find the enum type
            enum_info = next(
                (e for e in enum_infos if e.name == user_type_mapping.type_name),
                None,
            )
            if not enum_info:
                continue

            # Add the user enum type to the column
            column.user_enum_type = UserEnumType(
                name=enum_info.name,
                values=enum_info.values,
            )


def get_unique_columns_from_constraints(constraint: ConstraintInfo) -> list[str]:
    """Get unique columns from constraints."""
    # Extract column names from constraint definition
    # UNIQUE(column1, column2, ...) or UNIQUE (column1, column2, ...)
    match = re.match(r'UNIQUE[\s]*\((.*)\)', constraint.definition)
    if match:
        # Get the comma-separated list of columns
        columns_str = match.group(1).strip()
        # Split by comma and standardize column names
        return [standardize_column_name(col.strip()) or col.strip() for col in columns_str.split(',')]
    return []


def update_column_constraint_definitions(tables: dict) -> None:
    """Update columns with their CHECK constraint definitions."""
    for table in tables.values():
        for constraint in table.constraints:
            if constraint.type == 'c':  # Check constraint
                # Extract column name and definition from CHECK (column > 0)
                match = re.match(r'CHECK \(\(([^\)]+)\) (.*)\)', constraint.definition)
                if match:
                    column_name = match.group(1).strip()
                    check_definition = match.group(2).strip()
                    standardized_column_name = standardize_column_name(column_name) or column_name
                    column = next((c for c in table.columns if c.name == standardized_column_name), None)
                    if column:
                        column.check_definition = check_definition


def update_columns_with_constraints(tables: dict) -> None:
    """Update columns with constraints."""
    for table in tables.values():
        for constraint in table.constraints:
            if constraint.type == 'p':  # Primary key
                column_names = re.findall(r'\b(\w+)\b', constraint.definition)
                for column_name in column_names:
                    standardized_column_name = standardize_column_name(column_name) or column_name
                    column = next((c for c in table.columns if c.name == standardized_column_name), None)
                    if column:
                        column.primary = True
            elif constraint.type == 'u':  # Unique constraint
                column_names = get_unique_columns_from_constraints(constraint)
                for column_name in column_names:
                    column = next((c for c in table.columns if c.name == column_name), None)
                    if column:
                        column.unique = True


def determine_relationship_type(
    source_table: TableInfo, target_table: TableInfo, fk: ForeignKeyInfo
) -> tuple[RelationType, RelationType]:
    """Determine the relationship type between two tables based on their constraints.

    Args:
        source_table: The table containing the foreign key
        target_table: The table being referenced by the foreign key
        fk: The foreign key information

    Returns:
        A tuple of (forward_type, reverse_type) representing the relationship in both directions
    """
    # Get the column in the source table
    source_column = next((c for c in source_table.columns if c.name == fk.column_name), None)
    if not source_column:
        return RelationType.ONE_TO_MANY, RelationType.MANY_TO_ONE

    # Get the column in the target table
    target_column = next((c for c in target_table.columns if c.name == fk.foreign_column_name), None)
    if not target_column:
        return RelationType.ONE_TO_MANY, RelationType.MANY_TO_ONE

    # Check if the source column is a primary key or part of a composite primary key
    source_is_primary = source_column.primary
    source_is_unique = source_column.unique

    # Check if the target column is part of a primary key (usually it is)
    # This information might be used in future enhancements
    _ = target_column.primary

    # Check if the foreign key forms part of a composite unique key
    is_part_of_composite_unique = False
    for constraint in source_table.constraints:
        if constraint.type == 'u':  # Unique constraint
            unique_columns = get_unique_columns_from_constraints(constraint)
            if len(unique_columns) > 1 and fk.column_name in unique_columns:
                is_part_of_composite_unique = True
                break

    # ONE-TO-ONE: If the foreign key column is unique or primary in the source table
    if source_is_primary or source_is_unique or is_part_of_composite_unique:
        return RelationType.ONE_TO_ONE, RelationType.ONE_TO_ONE

    # MANY-TO-ONE: From source to target (default case for a foreign key)
    # ONE-TO-MANY: From target to source (inverse of the foreign key)
    return RelationType.MANY_TO_ONE, RelationType.ONE_TO_MANY


def analyze_table_relationships(tables: dict) -> None:
    """Analyze table relationships and determine relationship types."""
    processed_constraints = set()

    for table_key, table in tables.items():
        # Process each foreign key
        for fk in table.foreign_keys:
            # Skip if we already processed this constraint
            if fk.constraint_name in processed_constraints:
                continue

            # Find the foreign table
            foreign_table_key = next(
                (
                    tk
                    for tk, t in tables.items()
                    if t.name == fk.foreign_table_name and tk[0] == table_key[0]  # Same schema
                ),
                None,
            )
            if not foreign_table_key:
                continue

            foreign_table = tables[foreign_table_key]

            # Determine relationship type
            forward_type, reverse_type = determine_relationship_type(table, foreign_table, fk)

            # Update the relationship type
            fk.relation_type = forward_type

            # Handle the reverse relationship
            existing_fk = next((f for f in foreign_table.foreign_keys if f.constraint_name == fk.constraint_name), None)

            if existing_fk:
                # Update existing reverse foreign key
                existing_fk.relation_type = reverse_type
            else:
                # Create new reverse foreign key
                reverse_fk = ForeignKeyInfo(
                    constraint_name=fk.constraint_name,
                    column_name=fk.foreign_column_name,
                    foreign_table_name=table.name,
                    foreign_column_name=fk.column_name,
                    relation_type=reverse_type,
                )
                foreign_table.foreign_keys.append(reverse_fk)

            # Mark this constraint as processed
            processed_constraints.add(fk.constraint_name)


def is_bridge_table(table: TableInfo) -> bool:
    """Check if the table is a bridge table."""
    logging.debug(f'Analyzing if {table.name} is a bridge table')
    logging.debug(f'Foreign keys: {[fk.column_name for fk in table.foreign_keys]}')

    # Check for at least two foreign keys
    if len(table.foreign_keys) < 2:
        logging.debug('Not a bridge table: Less than 2 foreign keys')
        return False

    # Identify columns that are both primary keys and part of foreign keys
    primary_foreign_keys = [
        col.name
        for col in table.columns
        if col.primary and any(fk.column_name == col.name for fk in table.foreign_keys)
    ]
    logging.debug(f'Primary foreign keys: {primary_foreign_keys}')

    # Check if there are at least two such columns
    if len(primary_foreign_keys) < 2:
        logging.debug('Not a bridge table: Less than 2 primary foreign keys')
        return False

    # Get all primary key columns
    primary_keys = [col.name for col in table.columns if col.primary]
    logging.debug(f'All primary keys: {primary_keys}')

    # Consider the table a bridge table if the primary key is composite and includes at least two foreign key columns
    if len(primary_foreign_keys) == len(primary_keys):
        logging.debug('Is bridge table: All primary keys are foreign keys')
        return True

    logging.debug('Not a bridge table: Some primary keys are not foreign keys')
    return False


def analyze_bridge_tables(tables: dict) -> None:
    """Analyze if each table is a bridge table."""
    for table in tables.values():
        table.is_bridge = is_bridge_table(table)
        if table.is_bridge:
            # Update all foreign key relationships to MANY_TO_MANY
            for fk in table.foreign_keys:
                logging.debug(
                    f'Setting {table.name}.{fk.column_name} -> {fk.foreign_table_name}.{fk.foreign_column_name} to MANY_TO_MANY'  # noqa: E501
                )
                fk.relation_type = RelationType.MANY_TO_MANY


def construct_table_info(
    column_details: list,
    fk_details: list,
    constraints: list,
    enum_types: list,
    enum_type_mapping: list,
    schema: str = 'public',
) -> list[TableInfo]:
    """Construct TableInfo objects from column and foreign key details."""
    # Construct table information
    tables = get_table_details_from_columns(column_details)
    add_foreign_key_info_to_table_details(tables, fk_details)
    add_constraints_to_table_details(tables, schema, constraints)
    add_relationships_to_table_details(tables, fk_details)
    add_user_defined_types_to_tables(tables, schema, enum_types, enum_type_mapping)

    # Update columns with constraints
    update_columns_with_constraints(tables)
    update_column_constraint_definitions(tables)
    analyze_bridge_tables(tables)

    # Run analysis twice to ensure all relationships are captured
    analyze_table_relationships(tables)
    analyze_table_relationships(tables)

    return list(tables.values())
