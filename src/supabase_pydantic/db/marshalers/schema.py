import logging

from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.marshalers.abstract.base_column_marshaler import BaseColumnMarshaler
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
from supabase_pydantic.db.type_factory import TypeMapFactory

# Make sure logger is defined
logger = logging.getLogger(__name__)


def get_table_details_from_columns(
    column_details: list,
    enum_types: list[str] = [],
    disable_model_prefix_protection: bool = False,
    column_marshaler: BaseColumnMarshaler | None = None,
) -> dict[tuple[str, str], TableInfo]:
    """Get the table details from the column details.

    Args:
        column_details: List of column details from database query
        enum_types: Optional list of enum types from database to avoid warnings
        disable_model_prefix_protection: If True, don't protect model_ prefixed columns
        column_marshaler: Optional column marshaler to use for processing column types

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
            description,
        ) = row
        table_key: tuple[str, str] = (schema, table_name)
        if table_key not in tables:
            tables[table_key] = TableInfo(name=table_name, schema=schema, table_type=table_type)
        # Use the marshaler's method if provided, otherwise fallback to direct function call
        python_type = (
            column_marshaler.process_column_type(data_type, udt_name, enum_types=enum_types)
            if column_marshaler
            else process_udt_field(udt_name, data_type, known_enum_types=enum_types)
        )

        column_info = ColumnInfo(
            name=standardize_column_name(column_name, disable_model_prefix_protection) or column_name,
            alias=get_alias(column_name, disable_model_prefix_protection),
            post_gres_datatype=data_type,
            datatype=python_type,
            default=default,
            is_nullable=is_nullable == 'YES',
            max_length=max_length,
            is_identity=identity_generation is not None,
            array_element_type=array_element_type,
            description=description,
        )
        tables[table_key].add_column(column_info)

    return tables


def get_enum_types(enum_types: list, schema: str | None = None) -> list[UserEnumType]:
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
        if schema is not None and namespace != schema:
            continue
        if t == 'e':
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


def get_user_type_mappings(enum_type_mapping: list, schema: str | None = None) -> list[UserTypeMapping]:
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

        if schema is not None and namespace != schema:
            continue

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
    tables: dict[tuple[str, str], TableInfo],
    schema: str,
    enum_types: list,
    enum_type_mapping: list,
    db_type: DatabaseType = DatabaseType.POSTGRES,
) -> None:
    """Get user defined types and add them to ColumnInfo."""
    enums = get_enum_types(enum_types)
    mappings = get_user_type_mappings(enum_type_mapping)

    # Log available enums for debugging
    logger.debug(f'Available enum types: {[e.type_name for e in enums]}')

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
                                name=enum_info.type_name, values=enum_info.enum_values, schema=mapping.namespace
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
                clean_element_type = col.array_element_type
                if clean_element_type and clean_element_type.endswith('[]'):
                    clean_element_type = clean_element_type[:-2]  # Remove the trailing []

                logger.debug(f'Column {table.name}.{col.name} has array_element_type: {col.array_element_type}')
                logger.debug(f'Cleaned element type: {clean_element_type}')

                # Try to find a matching enum using our new helper method
                matched_enum = None

                # First, try exact match with our helper method
                for enum in enums:
                    if enum.matches_type_name(clean_element_type):
                        matched_enum = enum
                        logger.debug(f'✅ Matched enum {enum.type_name} for element type {clean_element_type}')
                        break
                    else:
                        logger.debug(f'❌ Failed to match {clean_element_type} with enum {enum.type_name}')

                # If no match, try a special case for _first_type/_second_type
                if not matched_enum and clean_element_type and clean_element_type.startswith('_'):
                    clean_name = clean_element_type.lstrip('_')
                    for enum in enums:
                        if enum.type_name.lower() == clean_name.lower():
                            matched_enum = enum
                            logger.debug(f'✅ Special case match: {clean_element_type} -> {enum.type_name}')
                            break
                        elif enum.type_name.lower() == clean_element_type.lower():
                            matched_enum = enum
                            logger.debug(f'✅ Direct match for {clean_element_type} with {enum.type_name}')
                            break

                if matched_enum:
                    col.enum_info = EnumInfo(
                        name=matched_enum.type_name, values=matched_enum.enum_values, schema=matched_enum.namespace
                    )
                else:
                    # Check if it's a standard PostgreSQL type before logging a warning
                    # Get the PostgreSQL type map
                    type_map = TypeMapFactory.get_pydantic_type_map(db_type)

                    # Check both the original type and the version without underscore
                    if clean_element_type in type_map or clean_element_type.lstrip('_') in type_map:
                        # It's a standard type, no need to warn
                        pass
                    else:
                        # Just log the element type that wasn't matched
                        logger.warning(f'Unknown array element type: {clean_element_type}, using Any')


def get_enum_types_by_schema(enum_types: list, schema: str) -> list[str]:
    """Get enum types by schema with proper normalization.

    Includes both original type names and normalized versions (with leading underscores removed)
    to ensure all possible matching patterns are included.
    """
    # Get the standard type names
    type_names = [e[0] for e in enum_types if e[1] == schema]

    # Also include versions with leading underscores removed
    normalized_names = []
    for name in type_names:
        # Include original name
        normalized_names.append(name)

        # Include version with leading underscores removed
        if name.startswith('_'):
            clean_name = name.lstrip('_')
            normalized_names.append(clean_name)
            logger.debug(f'Added normalized enum name: {name} -> {clean_name}')

    logger.debug(f'Normalized enum type list: {normalized_names}')
    return normalized_names


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
    tables = get_table_details_from_columns(
        column_details, get_enum_types_by_schema(enum_types, schema), disable_model_prefix_protection
    )
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
