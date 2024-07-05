import builtins
import keyword
from supabase_pydantic.util.constants import RelationType, PYDANTIC_TYPE_MAP
from supabase_pydantic.util.dataclasses import ColumnInfo, ConstraintInfo, ForeignKeyInfo, TableInfo


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


def get_table_details_from_columns(column_details: list) -> dict[str, TableInfo]:
    """Get the table details from the column details."""
    tables = {}
    for row in column_details:
        (schema, table_name, column_name, default, is_nullable, data_type, max_length) = row
        table_key = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema)
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
                foreign_column_name=foreign_column_name,
                relation_type=RelationType.ONE_TO_MANY,  # Simplified assumption
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
                        # primary key
                        if constraint.constraint_type() == 'PRIMARY KEY':
                            column.primary = True


def construct_table_info(column_details: list, fk_details: list, constraints: list) -> list[TableInfo]:
    """Construct TableInfo objects from column and foreign key details."""
    tables = get_table_details_from_columns(column_details)
    add_foreign_key_info_to_table_details(tables, fk_details)
    add_constraints_to_table_details(tables, constraints)
    update_columns_with_constraints(tables)
    return list(tables.values())
