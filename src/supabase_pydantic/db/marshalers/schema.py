from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.marshalers.column import get_alias, process_udt_field, standardize_column_name
from supabase_pydantic.db.marshalers.constraints import (
    add_constraints_to_table_details,
    update_column_constraint_definitions,
    update_columns_with_constraints,
)
from supabase_pydantic.db.marshalers.relationships import (
    add_foreign_key_info_to_table_details,
    add_relationships_to_table_details,
    analyze_bridge_tables,
    analyze_table_relationships,
)
from supabase_pydantic.db.models import ColumnInfo, TableInfo, UserEnumType, UserTypeMapping


def get_table_details_from_columns(
    column_details: list, disable_model_prefix_protection: bool = False
) -> dict[tuple[str, str], TableInfo]:
    """Get the table details from the column details.

    Args:
        column_details: List of column details from database query
        disable_model_prefix_protection: If True, don't protect model_ prefixed columns

    Returns:
        Dictionary mapping schema and table names to TableInfo objects
    """
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
            udt_name,
            array_element_type,
        ) = row
        table_key: tuple[str, str] = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema, table_type=table_type)
        column_info = ColumnInfo(
            name=standardize_column_name(column_name, disable_model_prefix_protection) or column_name,
            alias=get_alias(column_name, disable_model_prefix_protection),
            post_gres_datatype=data_type,
            datatype=process_udt_field(udt_name, data_type),
            default=default,
            is_nullable=is_nullable == 'YES',
            max_length=max_length,
            is_identity=identity_generation is not None,
            array_element_type=array_element_type,
        )
        tables[table_key].add_column(column_info)

    return tables


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

    # First, process direct enum mappings
    for mapping in mappings:
        table_key = (schema, mapping.table_name)
        enum_info = next((e for e in enums if e.type_name == mapping.type_name), None)
        enum_values = enum_info.enum_values if enum_info else None
        if table_key in tables:
            if mapping.column_name in [c.name for c in tables[table_key].columns]:
                for col in tables[table_key].columns:
                    if col.name == mapping.column_name:
                        col.user_defined_values = enum_values  # backward compatibility
                        col.enum_info = None
                        if enum_info:
                            col.enum_info = EnumInfo(
                                name=enum_info.type_name, values=enum_info.enum_values, schema=schema
                            )
                        break

    # Now, process array columns with enum element types
    for table_key, table in tables.items():
        for col in table.columns:
            # Skip columns that already have enum_info or are not arrays
            if col.enum_info is not None or not col.datatype.startswith('list['):
                continue

            # Check if this is an array column with array_element_type
            if col.array_element_type:
                # Clean up the array_element_type by removing array brackets if present
                clean_element_type = col.array_element_type
                if clean_element_type and clean_element_type.endswith('[]'):
                    clean_element_type = clean_element_type[:-2]  # Remove the trailing []

                for enum in enums:
                    if enum.type_name == clean_element_type:
                        col.enum_info = EnumInfo(name=enum.type_name, values=enum.enum_values, schema=table.schema)
                        break
                    else:
                        # Check if the array_element_type is a qualified type name (schema.typename)
                        # and extract just the type name part for comparison
                        if '.' in clean_element_type:
                            type_name = clean_element_type.split('.')[-1]
                            if enum.type_name == type_name:
                                col.enum_info = EnumInfo(
                                    name=enum.type_name, values=enum.enum_values, schema=table.schema
                                )
                                break


def construct_table_info(
    column_details: list,
    fk_details: list,
    constraints: list,
    # user_defined_types: list,
    enum_types: list,
    enum_type_mapping: list,
    schema: str = 'public',
    disable_model_prefix_protection: bool = False,
) -> list[TableInfo]:
    """Construct TableInfo objects from column and foreign key details.

    Args:
        column_details: List of column details from database query
        fk_details: List of foreign key details
        constraints: List of constraints
        enum_types: List of enum types
        enum_type_mapping: List of enum type mappings
        schema: Database schema name
        disable_model_prefix_protection: If True, don't prefix model_ fields

    Returns:
        List of TableInfo objects
    """
    # Construct table information
    tables = get_table_details_from_columns(column_details, disable_model_prefix_protection)
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
