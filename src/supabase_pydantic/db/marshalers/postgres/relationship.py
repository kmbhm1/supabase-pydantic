from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.marshalers.relationships import (
    analyze_table_relationships as analyze_relationships,
)
from supabase_pydantic.db.marshalers.relationships import (
    determine_relationship_type as determine_rel_type,
)
from supabase_pydantic.db.models import ForeignKeyInfo, TableInfo


class PostgresRelationshipMarshaler(BaseRelationshipMarshaler):
    """PostgreSQL implementation of relationship marshaler."""

    def determine_relationship_type(
        self, source_table: TableInfo, target_table: TableInfo, source_column: str, target_column: str
    ) -> RelationType:
        """Determine the type of relationship between two tables."""
        # Create a more meaningful constraint name based on tables and columns
        constraint_name = f'fk_{source_table.name}_{source_column}_to_{target_table.name}_{target_column}'

        # Create a ForeignKeyInfo object with the proper constraint name
        fk = ForeignKeyInfo(
            constraint_name=constraint_name,
            column_name=source_column,
            foreign_table_name=target_table.name,
            foreign_column_name=target_column,
            foreign_table_schema=target_table.schema,
        )
        forward_type, _ = determine_rel_type(source_table, target_table, fk)
        return forward_type

    def analyze_table_relationships(self, tables: dict[tuple[str, str], TableInfo]) -> None:
        """Analyze relationships between tables."""
        analyze_relationships(tables)
