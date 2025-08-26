from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.marshalers.relationships import (
    analyze_table_relationships as analyze_relationships,
)
from supabase_pydantic.db.models import TableInfo


class PostgresRelationshipMarshaler(BaseRelationshipMarshaler):
    """PostgreSQL implementation of relationship marshaler."""

    def determine_relationship_type(
        self, source_table: TableInfo, target_table: TableInfo, source_column: str, target_column: str
    ) -> RelationType:
        """Determine the type of relationship between two tables."""
        # Check if the source column is unique or primary key
        is_source_unique = any(
            col.name == source_column and (col.is_unique or col.primary) for col in source_table.columns
        )

        # Check if the target column is unique or primary key
        is_target_unique = any(
            col.name == target_column and (col.is_unique or col.primary) for col in target_table.columns
        )

        # Determine relationship type based on uniqueness
        if is_source_unique and is_target_unique:
            # If both sides are unique, it's a one-to-one relationship
            return RelationType.ONE_TO_ONE
        elif is_source_unique and not is_target_unique:
            # If only source is unique, it's one-to-many fr`om source to target
            return RelationType.ONE_TO_MANY
        elif not is_source_unique and is_target_unique:
            # If only target is unique, it's many-to-one from source to target
            return RelationType.MANY_TO_ONE
        else:
            # If neither side is unique, it's many-to-many
            return RelationType.MANY_TO_MANY

    def analyze_table_relationships(self, tables: dict[tuple[str, str], TableInfo]) -> None:
        """Analyze relationships between tables."""
        analyze_relationships(tables)
