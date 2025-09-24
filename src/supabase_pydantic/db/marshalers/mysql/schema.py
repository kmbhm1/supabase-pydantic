"""MySQL schema marshaler implementation."""

import logging
from typing import Any

from supabase_pydantic.core.models import EnumInfo
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.marshalers.abstract.base_column_marshaler import BaseColumnMarshaler
from supabase_pydantic.db.marshalers.abstract.base_constraint_marshaler import BaseConstraintMarshaler
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.marshalers.abstract.base_schema_marshaler import BaseSchemaMarshaler
from supabase_pydantic.db.marshalers.schema import (
    add_constraints_to_table_details,
    add_foreign_key_info_to_table_details,
    add_relationships_to_table_details,
    analyze_bridge_tables,
    analyze_table_relationships,
    get_table_details_from_columns,
    update_column_constraint_definitions,
    update_columns_with_constraints,
)
from supabase_pydantic.db.models import TableInfo, UserEnumType, UserTypeMapping

# Get Logger
logger = logging.getLogger(__name__)


def get_enum_types(enum_types: list, schema: str) -> list[UserEnumType]:
    """Get enum types from MySQL enum type data.

    This MySQL-specific version handles the structure returned by MySQL's enum query.

    Args:
        enum_types: List of enum type data rows from MySQL
        schema: Schema name

    Returns:
        List of UserEnumType objects
    """
    enums = []
    for row in enum_types:
        # Our modified MySQL ENUMS_QUERY now returns data in this structure
        if isinstance(row, dict):
            type_name = row.get('type_name')
            namespace = row.get('namespace')
            owner = row.get('owner')
            category = row.get('category')
            is_defined = row.get('is_defined')
            t = row.get('type')  # Should be 'e' for enum
            enum_values = row.get('enum_values')

            # Check if this is already a list, if not try to convert it
            if not isinstance(enum_values, list) and enum_values:
                logger.warning(f'Enum values for {type_name} not properly converted to list: {enum_values}')
        else:
            # Tuple unpacking for the standard format
            try:
                (
                    type_name,
                    namespace,
                    owner,
                    category,
                    is_defined,
                    t,  # type
                    enum_values,
                ) = row
            except ValueError as e:
                logger.error(f'Error unpacking enum type: {e}, row: {row}')
                continue

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


def add_mysql_user_defined_types_to_tables(
    tables: dict[tuple[str, str], TableInfo], schema: str, enums: list[UserEnumType], enum_type_mapping: list
) -> None:
    """Add user defined types from MySQL to tables.

    This MySQL-specific version handles pre-processed UserEnumType objects rather than raw data.

    Args:
        tables: Dictionary of tables by (schema, name) tuple
        schema: Schema name to filter enum types
        enums: List of already processed UserEnumType objects
        enum_type_mapping: List of mappings of columns to enum types
    """
    # Convert mappings to the expected format
    mappings = []
    for row in enum_type_mapping:
        if isinstance(row, dict):
            column_name = row.get('column_name')
            table_name = row.get('table_name')
            namespace = row.get('namespace')
            type_name = row.get('type_name')
            type_category = row.get('type_category')
            type_description = row.get('type_description')
        else:
            try:
                (
                    column_name,
                    table_name,
                    namespace,
                    type_name,
                    type_category,
                    type_description,
                ) = row
            except ValueError as e:
                logger.error(f'Error unpacking enum type mapping: {e}, row: {row}')
                continue

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
                # Clean up the array_element_type by removing array brackets if present
                clean_element_type = col.array_element_type
                if clean_element_type and clean_element_type.endswith('[]'):
                    clean_element_type = clean_element_type[:-2]  # Remove the trailing []

                for enum in enums:
                    if enum.type_name == clean_element_type:
                        col.enum_info = EnumInfo(name=enum.type_name, values=enum.enum_values, schema=enum.namespace)
                        break
                    else:
                        # Check if the array_element_type is a qualified type name (schema.typename)
                        # and extract just the type name part for comparison
                        if '.' in clean_element_type:
                            type_name = clean_element_type.split('.')[-1]
                            if enum.type_name == type_name:
                                col.enum_info = EnumInfo(
                                    name=enum.type_name, values=enum.enum_values, schema=enum.namespace
                                )
                                break


class MySQLSchemaMarshaler(BaseSchemaMarshaler):
    """MySQL schema marshaler implementation."""

    def __init__(
        self,
        column_marshaler: BaseColumnMarshaler,
        constraint_marshaler: BaseConstraintMarshaler,
        relationship_marshaler: BaseRelationshipMarshaler,
    ):
        """Initialize schema marshaler with component marshalers.

        Args:
            column_marshaler: Component for handling column details.
            constraint_marshaler: Component for handling constraint details.
            relationship_marshaler: Component for handling relationship details.
        """
        super().__init__(column_marshaler, constraint_marshaler, relationship_marshaler)
        self.db_type = DatabaseType.MYSQL

    def process_columns(self, column_data: list[dict[str, Any]]) -> list[tuple]:
        """Process column data from database-specific format.

        In MySQL, we need to adjust the column data to match the expected format.
        """
        # Convert MySQL-specific column data format to the common format
        # If the formats are compatible, this can just return the data
        processed_data = []
        for column in column_data:
            # Check if this is a result from GET_ALL_PUBLIC_TABLES_AND_COLUMNS query
            if 'TABLE_SCHEMA' in column and 'TABLE_NAME' in column:
                # Already in the correct format with all fields
                processed_data.append(
                    (
                        column.get('TABLE_SCHEMA'),
                        column.get('TABLE_NAME'),
                        column.get('COLUMN_NAME'),
                        column.get('COLUMN_DEFAULT'),
                        column.get('IS_NULLABLE'),
                        column.get('DATA_TYPE'),
                        column.get('CHARACTER_MAXIMUM_LENGTH'),
                        column.get('TABLE_TYPE', 'BASE TABLE'),
                        column.get('IDENTITY_GENERATION'),
                        column.get('UDT_NAME', column.get('DATA_TYPE')),
                        column.get('ARRAY_ELEMENT_TYPE'),
                        column.get('COLUMN_COMMENT', ''),  # Add column description/comment as 12th value
                    )
                )
            else:
                # Standard column format, we need to adjust it
                # Note: Missing table_schema and table_name here
                # This branch won't be used with our new approach
                logger.warning(
                    f"Column data missing table_schema and table_name: {column}. This branch won't be used with our new approach."  # noqa: E501
                )
                pass
        return processed_data

    def process_constraints(self, constraint_data: list[tuple]) -> list[tuple]:
        """Process constraint data from database-specific format."""
        return constraint_data

    def get_table_details_from_columns(self, column_data: list[dict[str, Any]]) -> dict[tuple[str, str], TableInfo]:
        """Get table details from column data.

        Args:
            column_data: List of column data from database.

        Returns:
            Dictionary mapping (schema, table) tuples to TableInfo objects.
        """
        # Process columns first
        processed_column_data = self.process_columns(column_data)

        # Get the disable_model_prefix_protection value from the instance or default to False
        disable_model_prefix_protection = getattr(self, 'disable_model_prefix_protection', False)

        # Call the common implementation
        result: dict[tuple[str, str], TableInfo] = get_table_details_from_columns(
            processed_column_data, disable_model_prefix_protection, column_marshaler=self.column_marshaler
        )
        return result

    def process_foreign_keys(self, tables: dict[tuple[str, str], TableInfo], fk_data: list[tuple]) -> None:
        """Add foreign key information to tables.

        Args:
            tables: Dictionary of table information objects.
            fk_data: Raw foreign key data from database.
        """
        # Process the foreign key data and add it to the tables
        add_foreign_key_info_to_table_details(tables, fk_data)

    def construct_table_info(
        self,
        table_data: list[dict[str, Any]],
        column_data: list[dict[str, Any]],
        fk_data: list[tuple],
        constraint_data: list[tuple],
        type_data: list[tuple],
        type_mapping_data: list[tuple],
        schema: str,
        disable_model_prefix_protection: bool = False,
    ) -> list[TableInfo]:
        """Construct TableInfo objects from database details."""
        # Debug logging for raw input data
        logger.debug(f"Constructing table info for schema '{schema}'")
        logger.debug(f'Raw table data count: {len(table_data)}')
        logger.debug(f'Raw column data count: {len(column_data)}')
        logger.debug(f'Raw foreign key count: {len(fk_data)}')
        logger.debug(f'Raw constraint count: {len(constraint_data)}')

        # Process the raw data
        processed_column_data = self.process_columns(column_data)
        logger.debug(f'Processed column data count: {len(processed_column_data)}')
        processed_constraint_data = self.process_constraints(constraint_data)

        # Construct table information
        tables = get_table_details_from_columns(
            column_details=processed_column_data,
            disable_model_prefix_protection=disable_model_prefix_protection,
            column_marshaler=self.column_marshaler,
            enum_types=type_data,
        )
        logger.debug(f'Tables extracted from columns: {list(tables.keys())}')
        add_foreign_key_info_to_table_details(tables, fk_data)
        add_constraints_to_table_details(tables, schema, processed_constraint_data)
        add_relationships_to_table_details(tables, fk_data)

        # Use MySQL-specific get_enum_types function
        mysql_enums = get_enum_types(type_data, schema)

        # Use MySQL-specific add_user_defined_types function that doesn't reprocess enums
        add_mysql_user_defined_types_to_tables(tables, schema, mysql_enums, type_mapping_data)

        # Update columns with constraints
        update_columns_with_constraints(tables)
        update_column_constraint_definitions(tables)
        analyze_bridge_tables(tables)
        for _ in range(2):
            analyze_table_relationships(tables)  # run twice to ensure all relationships are captured

        return list(tables.values())
