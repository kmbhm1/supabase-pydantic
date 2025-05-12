import builtins
import keyword
import logging
import pprint
import re

from src.supabase_pydantic.utils.constants import PYDANTIC_TYPE_MAP, RelationType
from src.supabase_pydantic.utils.dataclasses import (
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
            datatype=PYDANTIC_TYPE_MAP.get(data_type, ('Any, from typing import Any'))[0],
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
            logging.warning(
                f'Skipping foreign key {constraint_name}: '
                f'Table {table_schema}.{table_name} -> {foreign_table_schema}.{foreign_table_name} not found'
            )
            continue

        # Get the tables
        table = tables[table_key]
        foreign_table = tables[foreign_table_key]

        # Find the columns in the tables
        column = next((c for c in table.columns if c.name == standardize_column_name(column_name)), None)
        foreign_column = next(
            (c for c in foreign_table.columns if c.name == standardize_column_name(foreign_column_name)), None
        )

        # Skip if either column is missing
        if not column or not foreign_column:
            logging.warning(
                f'Skipping foreign key {constraint_name}: Column {column_name} -> {foreign_column_name} not found'
            )
            continue

        # Determine relationship type
        forward_type, reverse_type = determine_relationship_type(table, foreign_table, column_name, foreign_column_name)

        # Add foreign key info to tables
        fk = ForeignKeyInfo(
            constraint_name=constraint_name,
            column_name=column_name,
            foreign_table_name=foreign_table_name,
            foreign_column_name=foreign_column_name,
            foreign_table_schema=foreign_table_schema,
            relation_type=forward_type,
        )
        table.add_foreign_key(fk)

        # Mark the column as a foreign key
        column.is_foreign_key = True

        # Creates a reverse foreign key for the relationship
        # It's technically not a real foreign key in the DB, but it helps with relationship modeling
        reverse_fk = ForeignKeyInfo(
            constraint_name=constraint_name + '_reverse',
            column_name=foreign_column_name,
            foreign_table_name=table_name,
            foreign_column_name=column_name,
            foreign_table_schema=table_schema,
            relation_type=reverse_type,
        )
        foreign_table.add_foreign_key(reverse_fk)


def add_constraints_to_table_details(tables: dict, schema: str, constraints: list) -> None:
    """Add constraints to the table details."""
    for constraint_row in constraints:
        (
            constraint_name,
            table_name,
            columns,
            constraint_type,
            constraint_definition,
        ) = constraint_row

        # Find the table
        table_key = next(
            (
                tk
                for tk in tables
                if schema == tk[0]
                and (table_name == tk[1] or table_name == f'"{schema}"."{tk[1]}"' or table_name == f'{schema}.{tk[1]}')
            ),
            None,
        )
        if not table_key:
            logging.warning(f'Skipping constraint {constraint_name}: Table {schema}.{table_name} not found')
            continue

        # Create the constraint and add it to the table
        constraint = ConstraintInfo(
            constraint_name=constraint_name,
            raw_constraint_type=constraint_type,
            constraint_definition=constraint_definition,
            columns=columns,
        )

        tables[table_key].add_constraint(constraint)


def add_relationships_to_table_details(tables: dict, fk_details: list) -> None:
    """Add relationships to the table details."""
    # First, extract relationship info from foreign keys
    relationships = {}
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

        # Create a key for the relationship
        relationship_key = (
            (table_schema, table_name, column_name),
            (foreign_table_schema, foreign_table_name, foreign_column_name),
        )

        # Determine relationship type based on constraints and cardinality
        table_key = (table_schema, table_name)
        foreign_table_key = (foreign_table_schema, foreign_table_name)

        # Skip if either table is missing
        if table_key not in tables or foreign_table_key not in tables:
            continue

        # Get the tables
        table = tables[table_key]
        foreign_table = tables[foreign_table_key]

        # Find the columns and check if they are part of a primary key
        source_column = next((c for c in table.columns if c.name == standardize_column_name(column_name)), None)
        target_column = next(
            (c for c in foreign_table.columns if c.name == standardize_column_name(foreign_column_name)), None
        )

        if not source_column or not target_column:
            continue

        # Get the primary keys for both tables
        source_primary_keys = [col.name for col in table.columns if col.primary]
        target_primary_keys = [col.name for col in foreign_table.columns if col.primary]

        # Check if the columns are part of the primary keys
        source_is_primary = source_column.name in source_primary_keys
        target_is_primary = target_column.name in target_primary_keys

        # Determine relationship type based on whether columns are part of primary keys
        relation_type = None
        if source_is_primary and target_is_primary:
            relation_type = RelationType.ONE_TO_ONE
        elif source_is_primary:
            relation_type = RelationType.MANY_TO_ONE
        elif target_is_primary:
            relation_type = RelationType.ONE_TO_MANY
        else:
            relation_type = RelationType.MANY_TO_MANY

        # Create relationship info
        relationship = RelationshipInfo(
            table_name=table_name,
            related_table_name=foreign_table_name,
            relation_type=relation_type,
        )

        # Store the relationship
        relationships[relationship_key] = relationship

    # Add the relationships to the tables
    for (source_schema, source_table, _), (target_schema, target_table, _) in relationships:
        source_key = (source_schema, source_table)
        target_key = (target_schema, target_table)

        if source_key in tables and target_key in tables:
            relationship = relationships[((source_schema, source_table, _), (target_schema, target_table, _))]
            tables[source_key].relationships.append(relationship)


def get_enum_types(enum_types: list, schema: str) -> list[UserEnumType]:
    """Get enum types."""
    result = []
    for row in enum_types:
        if len(row) != 7:
            logging.warning(f'Skipping enum type with unexpected row format: {row}')
            continue

        (
            type_name,
            namespace,
            owner,
            category,
            is_defined,
            type_,
            enum_values,
        ) = row

        # Skip if not in the specified schema
        namespace_parts = namespace.split('.')
        enum_schema = namespace_parts[-1] if namespace_parts else None
        if enum_schema != schema and schema != '*':
            continue

        user_enum_type = UserEnumType(
            type_name=type_name,
            namespace=namespace,
            owner=owner,
            category=category,
            is_defined=is_defined,
            type=type_,
            enum_values=enum_values or [],
        )
        result.append(user_enum_type)

    return result


def get_user_type_mappings(enum_type_mapping: list, schema: str) -> list[UserTypeMapping]:
    """Get user type mappings."""
    result = []
    for row in enum_type_mapping:
        if len(row) != 6:
            logging.warning(f'Skipping user type mapping with unexpected row format: {row}')
            continue

        (
            column_name,
            table_name,
            namespace,
            type_name,
            type_category,
            type_description,
        ) = row

        # Skip if not in the specified schema
        namespace_parts = namespace.split('.')
        mapping_schema = namespace_parts[-1] if namespace_parts else None
        if mapping_schema != schema and schema != '*':
            continue

        user_type_mapping = UserTypeMapping(
            column_name=column_name,
            table_name=table_name,
            namespace=namespace,
            type_name=type_name,
            type_category=type_category,
            type_description=type_description,
        )
        result.append(user_type_mapping)

    return result


def add_user_defined_types_to_tables(
    tables: dict[tuple[str, str], TableInfo], schema: str, enum_types: list, enum_type_mapping: list
) -> None:
    """Get user defined types and add them to ColumnInfo."""
    # First, get the enum types and type mappings
    user_enum_types = get_enum_types(enum_types, schema)
    user_type_mappings = get_user_type_mappings(enum_type_mapping, schema)

    # Then, iterate through the type mappings and update columns
    for mapping in user_type_mappings:
        # Find the table by name in the current schema
        table_keys = [tk for tk in tables if tk[0] == schema and tk[1] == mapping.table_name]
        if not table_keys:
            continue

        table = tables[table_keys[0]]

        # Find the column in the table
        column = next(
            (c for c in table.columns if c.name == standardize_column_name(mapping.column_name)),
            None,
        )
        if not column:
            continue

        # Find the corresponding enum type
        enum_type = next((e for e in user_enum_types if e.type_name == mapping.type_name), None)
        if not enum_type or not enum_type.enum_values:
            continue

        # Update the column with user-defined values (for enums)
        column.user_defined_values = enum_type.enum_values
        column.enum_info = EnumInfo(
            name=enum_type.type_name,
            values=enum_type.enum_values,
            schema=mapping.namespace.split('.')[-1] if '.' in mapping.namespace else mapping.namespace,
        )


def get_unique_columns_from_constraints(constraint: ConstraintInfo) -> list[str]:
    """Get unique columns from constraints."""
    if constraint.constraint_type() == 'UNIQUE':
        return constraint.columns

    # Look for UNIQUE constraints in the constraint definition
    if 'UNIQUE' in constraint.constraint_definition:
        match = re.search(r'UNIQUE \(([^)]+)\)', constraint.constraint_definition)
        if match:
            return [col.strip() for col in match.group(1).split(',')]

    return []


def update_column_constraint_definitions(tables: dict) -> None:
    """Update columns with their CHECK constraint definitions."""
    for table in tables.values():
        for constraint in table.constraints:
            if constraint.constraint_type() == 'CHECK':
                for col_name in constraint.columns:
                    column = next((c for c in table.columns if c.name == standardize_column_name(col_name)), None)
                    if column:
                        column.constraint_definition = constraint.constraint_definition


def update_columns_with_constraints(tables: dict) -> None:
    """Update columns with constraints."""
    for table in tables.values():
        # Get primary key columns
        primary_key_columns = set()
        for constraint in table.constraints:
            if constraint.constraint_type() == 'PRIMARY KEY':
                primary_key_columns.update(constraint.columns)

        # Get unique columns
        unique_columns = set()
        for constraint in table.constraints:
            if constraint.constraint_type() == 'UNIQUE':
                for col in constraint.columns:
                    # If there are multiple columns in this constraint, we need to track partners
                    if len(constraint.columns) > 1:
                        column = next((c for c in table.columns if c.name == standardize_column_name(col)), None)
                        if column:
                            column.unique_partners.extend(
                                [c for c in constraint.columns if c != col and c not in column.unique_partners]
                            )
                    unique_columns.add(col)

        # Update columns
        for column in table.columns:
            # Set primary key flag
            if column.name in primary_key_columns or any(col == column.name for col in primary_key_columns):
                column.primary = True

            # Set unique flag (for single-column unique constraints)
            if column.name in unique_columns and not column.unique_partners:
                column.is_unique = True


def determine_relationship_type(
    source_table: TableInfo, target_table: TableInfo, source_column: str, target_column: str
) -> tuple[RelationType, RelationType]:
    """Determine the relationship type between two tables based on their constraints.

    Args:
        source_table: The table containing the foreign key
        target_table: The table being referenced by the foreign key
        source_column: The column in the source table with the foreign key
        target_column: The column in the target table referenced by the foreign key

    Returns:
        A tuple of (forward_type, reverse_type) representing the relationship in both directions
    """
    # Get standardized column names
    std_source_column = standardize_column_name(source_column) or source_column
    std_target_column = standardize_column_name(target_column) or target_column

    # Get the actual column objects
    source_col_obj = next((c for c in source_table.columns if c.name == std_source_column), None)
    target_col_obj = next((c for c in target_table.columns if c.name == std_target_column), None)

    if not source_col_obj or not target_col_obj:
        # Default to ONE_TO_MANY if columns not found
        return RelationType.ONE_TO_MANY, RelationType.MANY_TO_ONE

    # Check if columns are part of primary keys
    source_primary = source_col_obj.primary
    target_primary = target_col_obj.primary

    # Check if columns have unique constraints (single-column or with partners)
    source_unique = source_col_obj.is_unique or source_col_obj.unique_partners
    target_unique = target_col_obj.is_unique or target_col_obj.unique_partners

    # Determine relationship type based on primary key and uniqueness
    if (source_primary or source_unique) and (target_primary or target_unique):
        # Both columns are primary or unique, so it's a ONE_TO_ONE relationship
        return RelationType.ONE_TO_ONE, RelationType.ONE_TO_ONE
    elif source_primary or source_unique:
        # Source column is primary or unique, so it's a ONE_TO_MANY relationship (from source to target)
        return RelationType.ONE_TO_MANY, RelationType.MANY_TO_ONE
    elif target_primary or target_unique:
        # Target column is primary or unique, so it's a MANY_TO_ONE relationship (from source to target)
        return RelationType.MANY_TO_ONE, RelationType.ONE_TO_MANY
    else:
        # Neither column is primary or unique, so it's a MANY_TO_MANY relationship
        return RelationType.MANY_TO_MANY, RelationType.MANY_TO_MANY


def analyze_table_relationships(tables: dict) -> None:
    """Analyze table relationships."""
    # Keep track of constraints we've already processed
    processed_constraints = set()

    # Iterate through all tables and foreign keys
    for table_key, table in tables.items():
        for fk in table.foreign_keys:
            # Skip if we've already processed this constraint
            if fk.constraint_name in processed_constraints:
                continue

            # Skip if we don't have relationship info yet
            if not fk.relation_type:
                continue

            # Find the target table
            foreign_table_key = next(
                (tk for tk in tables if tk[1] == fk.foreign_table_name),
                None,
            )
            if not foreign_table_key:
                continue

            foreign_table = tables[foreign_table_key]

            # Determine relationship types based on constraints
            forward_type, reverse_type = determine_relationship_type(
                table, foreign_table, fk.column_name, fk.foreign_column_name
            )

            # Update foreign key with the determined relationship type
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
    # user_defined_types: list,
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
    for _ in range(2):
        # TODO: update this fn to avoid running twice.
        # print('running analyze_table_relationships ' + str(i))
        analyze_table_relationships(tables)  # run twice to ensure all relationships are captured

    return list(tables.values())
