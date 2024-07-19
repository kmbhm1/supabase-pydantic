import builtins
import keyword
import pprint
import re
from supabase_pydantic.util.constants import RelationType, PYDANTIC_TYPE_MAP
from supabase_pydantic.util.dataclasses import ColumnInfo, ConstraintInfo, ForeignKeyInfo, TableInfo

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


def get_table_details_from_columns(column_details: list) -> dict[str, TableInfo]:
    """Get the table details from the column details."""
    tables = {}
    for row in column_details:
        (schema, table_name, column_name, default, is_nullable, data_type, max_length, table_type) = row
        table_key = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema, table_type=table_type)
        column_info = ColumnInfo(
            name=standardize_column_name(column_name),
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
                column_name=standardize_column_name(column_name),
                foreign_table_name=foreign_table_name,
                foreign_column_name=standardize_column_name(foreign_column_name),
                relation_type=None,
                foreign_table_schema=foreign_table_schema,
            )
            tables[table_key].add_foreign_key(fk_info)


def add_constraints_to_table_details(tables: dict, constraints: list) -> None:
    """Add constraints to the table details."""
    for row in constraints:
        (constraint_name, table_name, columns, constraint_type, constraint_definition) = row
        table_key = ('public', table_name)
        if table_key in tables:
            constraint = ConstraintInfo(
                constraint_name=constraint_name,
                columns=[standardize_column_name(c) for c in columns],
                raw_constraint_type=constraint_type,
                constraint_definition=constraint_definition,
            )
            tables[table_key].add_constraint(constraint)


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

            # TODO: for testing
            # print(
            #     table.name,
            #     fk.foreign_table_name,
            #     fk.foreign_column_name,
            #     f'1:1 test={(is_source_unique or is_source_foreign_key) and (is_target_primary or is_target_unique)}',
            #     f'target_primary={is_target_primary}',
            #     f'target_unique={is_target_unique}',
            #     f'target_foreign_key={is_target_foreign_key}',
            #     f'source_unique={is_source_unique}',
            #     f'source_foreign_key={is_source_foreign_key}',
            # )

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


def construct_table_info(column_details: list, fk_details: list, constraints: list) -> list[TableInfo]:
    """Construct TableInfo objects from column and foreign key details."""
    # construction
    tables = get_table_details_from_columns(column_details)
    add_foreign_key_info_to_table_details(tables, fk_details)
    add_constraints_to_table_details(tables, constraints)

    # updating
    update_columns_with_constraints(tables)
    analyze_bridge_tables(tables)
    for i in range(2):
        # TODO: update this fn to avoid running twice.
        print('running analyze_table_relationships ' + str(i))
        analyze_table_relationships(tables)  # run twice to ensure all relationships are captured

    # return
    return list(tables.values())
