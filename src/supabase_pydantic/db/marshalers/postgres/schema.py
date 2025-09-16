from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.marshalers.abstract.base_schema_marshaler import BaseSchemaMarshaler
from supabase_pydantic.db.marshalers.schema import (
    add_constraints_to_table_details,
    add_foreign_key_info_to_table_details,
    add_relationships_to_table_details,
    add_user_defined_types_to_tables,
    analyze_bridge_tables,
    analyze_table_relationships,
    get_enum_types_by_schema,
    get_table_details_from_columns,
    update_column_constraint_definitions,
    update_columns_with_constraints,
)
from supabase_pydantic.db.models import TableInfo


class PostgresSchemaMarshaler(BaseSchemaMarshaler):
    """PostgreSQL-specific implementation of schema marshaling."""

    def process_columns(self, column_data: list[tuple]) -> list[tuple]:
        """Process column data from database-specific format.

        In PostgreSQL, we can use the column data as is.
        """
        return column_data

    def process_foreign_keys(self, fk_data: list[tuple]) -> list[tuple]:
        """Process foreign key data from database-specific format.

        In PostgreSQL, we can use the foreign key data as is.
        """
        return fk_data

    def process_constraints(self, constraint_data: list[tuple]) -> list[tuple]:
        """Process constraint data from database-specific format.

        In PostgreSQL, we can use the constraint data as is.
        """
        return constraint_data

    def get_table_details_from_columns(self, column_data: list[tuple]) -> dict[tuple[str, str], TableInfo]:
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
        # Get table details using common function
        result: dict[tuple[str, str], TableInfo] = get_table_details_from_columns(
            processed_column_data, disable_model_prefix_protection, column_marshaler=self.column_marshaler
        )
        return result

    def construct_table_info(
        self,
        table_data: list[tuple],
        column_data: list[tuple],
        fk_data: list[tuple],
        constraint_data: list[tuple],
        type_data: list[tuple],
        type_mapping_data: list[tuple],
        schema: str,
        disable_model_prefix_protection: bool = False,
    ) -> list[TableInfo]:
        """Construct TableInfo objects from database details."""
        # Process the raw data
        processed_column_data = self.process_columns(column_data)
        processed_fk_data = self.process_foreign_keys(fk_data)
        processed_constraint_data = self.process_constraints(constraint_data)

        # Construct table information
        enum_types = get_enum_types_by_schema(type_data, schema)
        tables = get_table_details_from_columns(
            column_details=processed_column_data,
            disable_model_prefix_protection=disable_model_prefix_protection,
            column_marshaler=self.column_marshaler,
            enum_types=enum_types,
        )
        add_foreign_key_info_to_table_details(tables, processed_fk_data)
        add_constraints_to_table_details(tables, schema, processed_constraint_data)
        add_relationships_to_table_details(tables, processed_fk_data)
        add_user_defined_types_to_tables(tables, schema, type_data, type_mapping_data, DatabaseType.POSTGRES)

        # Update columns with constraints
        update_columns_with_constraints(tables)
        update_column_constraint_definitions(tables)
        analyze_bridge_tables(tables)
        for _ in range(2):
            # TODO: update this fn to avoid running twice.
            # print('running analyze_table_relationships ' + str(i))
            analyze_table_relationships(tables)  # run twice to ensure all relationships are captured

        return list(tables.values())
