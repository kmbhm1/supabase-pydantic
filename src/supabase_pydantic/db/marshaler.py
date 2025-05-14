"""Database metadata marshaling utilities.

This module contains functions for:
1. Analyzing database table relationships
2. Constructing TableInfo objects from database metadata
3. Handling column naming conventions and reserved keywords
4. Processing foreign key relationships and constraints
5. Detecting bridge tables and relationship types
"""

import builtins
import keyword
import logging
import pprint
import re

from src.supabase_pydantic.db.constants import PYDANTIC_TYPE_MAP, RelationType
from src.supabase_pydantic.db.models import (
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
    # Get the column in the source table that has the foreign key
    source_column = next((c for c in source_table.columns if c.name == fk.column_name), None)
    if source_column is None:
        return RelationType.UNDEFINED, RelationType.UNDEFINED

    # Get the column in the target table that is referenced by the foreign key
    target_column = next((c for c in target_table.columns if c.name == fk.foreign_column_name), None)
    if target_column is None:
        return RelationType.UNDEFINED, RelationType.UNDEFINED

    # If the target column is not a primary key, we can't determine the relationship
    if not target_column.primary:
        return RelationType.UNDEFINED, RelationType.UNDEFINED

    # If the source column is a primary key, it's ONE_TO_ONE
    if source_column.primary:
        return RelationType.ONE_TO_ONE, RelationType.ONE_TO_ONE

    # If the source column is unique, it's ONE_TO_ONE
    if source_column.is_unique:
        return RelationType.ONE_TO_ONE, RelationType.ONE_TO_ONE

    # Otherwise, it's MANY_TO_ONE
    return RelationType.MANY_TO_ONE, RelationType.ONE_TO_MANY


def add_foreign_key_info_to_table_details(tables: dict, fk_details: list) -> None:
    """Add foreign key information to the table details."""
    for row in fk_details:
        (
            schema,
            table_name,
            constraint_name,
            constraint_definition,
        ) = row
        table_key = (schema, table_name)
        if table_key not in tables:
            logging.warning(f'Table {table_key} not found in tables dict when adding foreign keys')
            continue

        # Parse foreign key constraint definition
        fk_parts = parse_constraint_definition_for_fk(constraint_definition)
        if not fk_parts:
            logging.warning(f'Could not parse foreign key constraint: {constraint_definition}')
            continue

        column_name, foreign_table_name, foreign_column_name = fk_parts

        # Standardize column names to match our schema model
        column_name = standardize_column_name(column_name) or column_name
        foreign_column_name = standardize_column_name(foreign_column_name) or foreign_column_name

        # Extract the schema if it's a fully qualified name
        if '.' in foreign_table_name:
            foreign_schema, foreign_table_name = foreign_table_name.split('.', 1)
            foreign_table_key = (foreign_schema, foreign_table_name)
        else:
            foreign_table_key = (schema, foreign_table_name)

        # Create FK info and add it to the table
        fk_info = ForeignKeyInfo(
            column_name=column_name,
            constraint_name=constraint_name,
            foreign_schema=foreign_table_key[0],
            foreign_table_name=foreign_table_name,
            foreign_column_name=foreign_column_name,
        )
        tables[table_key].add_foreign_key(fk_info)


def add_constraints_to_table_details(tables: dict, schema: str, constraints: list) -> None:
    """Add constraint information to the table details."""
    for row in constraints:
        (
            constraint_schema,
            table_name,
            constraint_name,
            constraint_type,
            column_name,
            constraint_definition,
        ) = row

        table_key = (constraint_schema, table_name)
        if table_key not in tables:
            logging.warning(f'Table {table_key} not found in tables dict when adding constraints')
            continue

        # Standardize column name
        column_name = standardize_column_name(column_name) or column_name

        # Create constraint info and add it to the table
        constraint_info = ConstraintInfo(
            name=constraint_name,
            type=constraint_type,
            column_name=column_name,
            definition=constraint_definition,
        )
        tables[table_key].add_constraint(constraint_info)


def add_relationships_to_table_details(tables: dict, fk_details: list) -> None:
    """Add relationship information to the table details.

    This establishes the bidirectional relationships between tables.
    """
    for table_key, table in tables.items():
        for fk in table.foreign_keys:
            foreign_table_key = (fk.foreign_schema, fk.foreign_table_name)
            if foreign_table_key not in tables:
                logging.warning(f'Foreign table {foreign_table_key} not found in tables dict')
                continue

            # Get the two tables involved in the relationship
            source_table = table
            target_table = tables[foreign_table_key]

            # Determine relationship type
            forward_type, reverse_type = determine_relationship_type(source_table, target_table, fk)
            fk.relation_type = forward_type

            # Create relationship info objects for both tables
            source_to_target = RelationshipInfo(
                source_table=table.name,
                source_schema=table.schema,
                source_column=fk.column_name,
                target_table=fk.foreign_table_name,
                target_schema=fk.foreign_schema,
                target_column=fk.foreign_column_name,
                relation_type=forward_type,
            )

            target_to_source = RelationshipInfo(
                source_table=fk.foreign_table_name,
                source_schema=fk.foreign_schema,
                source_column=fk.foreign_column_name,
                target_table=table.name,
                target_schema=table.schema,
                target_column=fk.column_name,
                relation_type=reverse_type,
            )

            # Add relationships to the tables
            source_table.add_relationship(source_to_target)
            target_table.add_relationship(target_to_source)


def is_bridge_table(table: TableInfo) -> bool:
    """Check if the table is a bridge table.

    Bridge tables are used to represent many-to-many relationships between entities.
    These are identified by having primary keys that are composed of foreign keys
    pointing to different tables.
    """
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


def add_user_defined_types_to_tables(tables: dict, schema: str, enum_types: list, enum_type_mapping: list) -> None:
    """Add user-defined types to the table details."""
    # Process enum types
    enums = {}
    for row in enum_types:
        enum_name, enum_values = row
        enums[enum_name] = UserEnumType(name=enum_name, values=enum_values)

    # Add enum types to tables and columns
    for row in enum_type_mapping:
        table_name, column_name, data_type = row
        table_key = (schema, table_name)
        if table_key not in tables:
            logging.warning(f'Table {table_key} not found in tables dict when adding user types')
            continue

        # Standardize column name
        column_name = standardize_column_name(column_name) or column_name

        column = tables[table_key].get_column(column_name)
        if not column:
            logging.warning(f'Column {column_name} not found in table {table_key}')
            continue

        if data_type in enums:
            enum_info = EnumInfo(
                name=data_type,
                values=enums[data_type].values,
            )
            tables[table_key].add_enum(enum_info)
            column.user_type = UserTypeMapping(data_type=data_type, enum_type=enum_info)


def update_columns_with_constraints(tables: dict) -> None:
    """Update columns with constraint information."""
    for table in tables.values():
        # Process all constraints for this table
        for constraint in table.constraints:
            # Only process constraints that are tied to a specific column
            if not constraint.column_name:
                continue

            # Find the column
            column = table.get_column(constraint.column_name)
            if not column:
                logging.warning(f'Column {constraint.column_name} not found in table {table.name} for constraint')
                continue

            # Apply constraint properties to the column
            if constraint.type == 'PRIMARY KEY':
                column.primary = True
            elif constraint.type == 'UNIQUE':
                column.is_unique = True
            elif constraint.type == 'CHECK':
                column.check_constraint = constraint.definition


def update_column_constraint_definitions(tables: dict) -> None:
    """Update columns with constraint definitions."""
    for table in tables.values():
        # Update foreign key columns with relationship information
        for fk in table.foreign_keys:
            column = table.get_column(fk.column_name)
            if column:
                column.is_foreign_key = True
                column.foreign_key_target = (fk.foreign_schema, fk.foreign_table_name, fk.foreign_column_name)


def analyze_table_relationships(tables: dict) -> None:
    """Analyze table relationships to determine the relationship types."""
    for table in tables.values():
        for rel in table.relationships:
            # Skip relationships that have already been classified
            if rel.relation_type != RelationType.UNDEFINED:
                continue

            # Get the two tables involved in the relationship
            source_table = table
            target_table_key = (rel.target_schema, rel.target_table)
            if target_table_key not in tables:
                logging.warning(f'Target table {target_table_key} not found in tables dict')
                continue

            target_table = tables[target_table_key]

            # Find the foreign key that corresponds to this relationship
            matching_fk = None
            for fk in source_table.foreign_keys:
                if (
                    fk.column_name == rel.source_column
                    and fk.foreign_table_name == rel.target_table
                    and fk.foreign_column_name == rel.target_column
                ):
                    matching_fk = fk
                    break

            if not matching_fk:
                logging.warning(f'Could not find matching FK for relationship {rel}')
                continue

            # Determine relationship type
            forward_type, reverse_type = determine_relationship_type(source_table, target_table, matching_fk)

            # Update relationship types
            rel.relation_type = forward_type

            # Find and update the reverse relationship
            for reverse_rel in target_table.relationships:
                if (
                    reverse_rel.source_column == rel.target_column
                    and reverse_rel.target_table == rel.source_table
                    and reverse_rel.target_column == rel.source_column
                ):
                    reverse_rel.relation_type = reverse_type
                    break


def analyze_bridge_tables(tables: dict) -> None:
    """Analyze if each table is a bridge table.

    This is important for correctly identifying many-to-many relationships,
    which require special handling in the model generation.
    """
    for table in tables.values():
        table.is_bridge = is_bridge_table(table)
        if table.is_bridge:
            # Update all foreign key relationships to MANY_TO_MANY
            for fk in table.foreign_keys:
                logging.debug(
                    f'Setting {table.name}.{fk.column_name} -> {fk.foreign_table_name}.{fk.foreign_column_name} to MANY_TO_MANY'  # noqa: E501
                )
                fk.relation_type = RelationType.MANY_TO_MANY


def get_enum_types(enum_types: list, schema: str) -> list[UserEnumType]:
    """Get enum types."""
    enums = []
    for row in enum_types:
        (
            type_name,
            namespace,
            owner,
            category,
            is_defined,
            t,  # type, typtype
            enum_values,
        ) = row
        if t == 'e' and namespace == schema:
            enums.append(
                UserEnumType(
                    type_name,
                    namespace,
                    owner,
                    category,
                    is_defined,
                    t,
                    enum_values,
                )
            )
    return enums


def get_user_type_mappings(enum_type_mapping: list, schema: str) -> list[UserTypeMapping]:
    """Get user type mappings."""
    return get_enum_type_mappings(enum_type_mapping, schema)


def get_enum_type_mappings(enum_type_mapping: list, schema: str) -> list[UserTypeMapping]:
    """Get enum type mappings."""
    mappings = []
    for row in enum_type_mapping:
        (
            column_name,
            table_name,
            namespace,
            type_name,
            type_category,
            type_description,
        ) = row
        if namespace == schema:
            mappings.append(
                UserTypeMapping(
                    column_name,
                    table_name,
                    namespace,
                    type_name,
                    type_category,
                    type_description,
                )
            )
    return mappings


def construct_table_info(
    column_details: list,
    fk_details: list,
    constraints: list,
    enum_types: list,
    enum_type_mapping: list,
    schema: str = 'public',
) -> list[TableInfo]:
    """Construct TableInfo objects from column and foreign key details.

    This is the main function that analyzes the database schema and generates a structured
    representation of all tables, columns, and their relationships. It properly detects
    relationship types (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY) which is used by model generators
    to create Pydantic models with the appropriate type annotations.
    """
    # Construct table information
    tables = get_table_details_from_columns(column_details)

    # Add foreign key information and relationships
    add_foreign_key_info_to_table_details(tables, fk_details)
    add_constraints_to_table_details(tables, schema, constraints)
    add_relationships_to_table_details(tables, fk_details)
    add_user_defined_types_to_tables(tables, schema, enum_types, enum_type_mapping)

    # Update columns with constraints
    update_columns_with_constraints(tables)
    update_column_constraint_definitions(tables)

    # Analyze table relationships
    analyze_bridge_tables(tables)
    analyze_table_relationships(tables)  # Detect ONE_TO_ONE, ONE_TO_MANY, etc.

    return list(tables.values())
