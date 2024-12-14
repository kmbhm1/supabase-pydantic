import builtins
import keyword
import pprint
import re
from typing import Any

from supabase_pydantic.util.constants import PYDANTIC_TYPE_MAP, RelationType
from supabase_pydantic.util.dataclasses import (
    ColumnInfo,
    ConstraintInfo,
    ForeignKeyInfo,
    RelationshipInfo,
    TableInfo,
    UserEnumType,
    UserTypeMapping,
)

pp = pprint.PrettyPrinter(indent=4)


def column_name_is_reserved(column_name: str) -> bool:
    """Check if the column name is a reserved keyword or built-in name or starts with model_."""
    return column_name in dir(builtins) or column_name in keyword.kwlist or column_name.startswith('model_')


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
        (schema, table_name, column_name, default, is_nullable, data_type, max_length, table_type) = row
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
        )
        tables[table_key].add_column(column_info)

    return tables


def add_foreign_key_info_to_table_details(tables: dict, fk_details: list) -> None:
    """Add foreign key information to the table details."""
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
        if table_key in tables:
            fk_info = ForeignKeyInfo(
                constraint_name=constraint_name,
                column_name=standardize_column_name(column_name) or column_name,
                foreign_table_name=foreign_table_name,
                foreign_column_name=standardize_column_name(foreign_column_name) or foreign_column_name,
                relation_type=None,
                foreign_table_schema=foreign_table_schema,
            )
            tables[table_key].add_foreign_key(fk_info)


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
        fk_columns = [fk for fk in tables[table_key].foreign_keys if fk.foreign_table_name == foreign_table_name]
        if len(fk_columns) == 1:
            # One-to-Many or One-to-One
            related_table_columns = [c.name for c in tables[foreign_table_key].columns]
            if fk_columns[0].foreign_column_name in related_table_columns:
                relation_type = RelationType.ONE_TO_ONE
            else:
                relation_type = RelationType.ONE_TO_MANY
        else:
            # Many-to-Many
            relation_type = RelationType.MANY_TO_MANY

        if table_key in tables:
            tables[table_key].relationships.append(
                RelationshipInfo(
                    **{
                        'table_name': table_key[1],
                        'related_table_name': foreign_table_key[1],
                        'relation_type': relation_type,
                    }
                )
            )
        else:
            print('Table key not found in tables', table_key)


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


def add_user_defined_types_to_tables(
    tables: dict[tuple[str, str], TableInfo], schema: str, enum_types: list, enum_type_mapping: list
) -> None:
    """Get user defined types and add them to ColumnInfo."""
    enums = get_enum_types(enum_types, schema)
    mappings = get_user_type_mappings(enum_type_mapping, schema)

    for mapping in mappings:
        table_key = (schema, mapping.table_name)
        enum_values = next((e.enum_values for e in enums if e.type_name == mapping.type_name), None)
        if table_key in tables:
            if mapping.column_name in [c.name for c in tables[table_key].columns]:
                for col in tables[table_key].columns:
                    if col.name == mapping.column_name:
                        col.user_defined_values = enum_values
                        break
            else:
                print('Column name not found in table columns for adding user defined values: ', mapping.column_name)
        else:
            print('Table key not found in tables for adding user defined values: ', tables[table_key])


def get_unique_columns_from_constraints(constraint: ConstraintInfo) -> list[str | Any]:
    """Get unique columns from constraints."""
    unique_columns = []
    if constraint.constraint_type() == 'UNIQUE':
        match = re.match(r'UNIQUE \(([^)]+)\)', constraint.constraint_definition)
        if match:
            columns = match.group(1).split(',')
            unique_columns = [c.strip() for c in columns]
    return unique_columns


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


def analyze_table_relationships(tables: dict) -> None:
    """Analyze table relationships."""
    for table in tables.values():
        for fk in table.foreign_keys:
            # Get the foreign table object based on the foreign_table_name and foreign_table_schema.
            foreign_table = next(
                (t for t in tables.values() if t.name == fk.foreign_table_name and t.schema == fk.foreign_table_schema),
                None,
            )
            if not foreign_table:
                continue  # Skip if no foreign table found

            # Checks
            is_target_primary = any(col.primary and col.name == fk.foreign_column_name for col in foreign_table.columns)
            is_target_unique = any(
                col.is_unique and col.name == fk.foreign_column_name for col in foreign_table.columns
            )
            is_target_foreign_key = any(
                col.is_foreign_key and col.name == fk.foreign_column_name for col in foreign_table.columns
            )
            is_source_unique = any(
                col.name == fk.column_name and (col.is_unique or col.primary) for col in table.columns
            )
            is_source_foreign_key = any(col.name == fk.column_name and col.is_foreign_key for col in table.columns)

            # Determine the initial relationship type from source to target
            if (is_source_unique or is_source_foreign_key) and (is_target_primary or is_target_unique):
                fk.relation_type = RelationType.ONE_TO_ONE  # Both sides are unique
            elif is_target_unique or is_target_primary or is_target_foreign_key:
                fk.relation_type = RelationType.ONE_TO_MANY
            else:
                fk.relation_type = RelationType.MANY_TO_MANY

            # Check for reciprocal foreign keys in the foreign table
            reciprocal_fks = [
                f
                for f in foreign_table.foreign_keys
                if f.foreign_table_name == table.name and f.foreign_column_name == fk.column_name
            ]
            if len(reciprocal_fks) > 1:
                fk.relation_type = RelationType.MANY_TO_MANY

            # Ensure the foreign table has a mirrored foreign key info for bidirectional clarity
            if not any(f.constraint_name == fk.constraint_name for f in foreign_table.foreign_keys):
                reverse_fk = ForeignKeyInfo(
                    constraint_name=fk.constraint_name,
                    column_name=fk.foreign_column_name,
                    foreign_table_name=table.name,
                    foreign_column_name=fk.column_name,
                    relation_type=fk.relation_type,
                )
                foreign_table.foreign_keys.append(reverse_fk)


def is_bridge_table(table: TableInfo) -> bool:
    """Check if the table is a bridge table."""
    # Check for at least two foreign keys
    if len(table.foreign_keys) < 2:
        return False

    # Identify columns that are both primary keys and part of foreign keys
    primary_foreign_keys = [
        col.name
        for col in table.columns
        if col.primary and any(fk.column_name == col.name for fk in table.foreign_keys)
    ]

    # Check if there are at least two such columns
    if len(primary_foreign_keys) < 2:
        return False

    # Consider the table a bridge table if the primary key is composite and includes at least two foreign key columns
    if len(primary_foreign_keys) == sum(1 for col in table.columns if col.primary):
        return True

    return False


def analyze_bridge_tables(tables: dict) -> None:
    """Analyze if each table is a bridge table."""
    for table in tables.values():
        table.is_bridge = is_bridge_table(table)


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
    analyze_bridge_tables(tables)
    for _ in range(2):
        # TODO: update this fn to avoid running twice.
        # print('running analyze_table_relationships ' + str(i))
        analyze_table_relationships(tables)  # run twice to ensure all relationships are captured

    return list(tables.values())
