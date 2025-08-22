"""MySQL relationship marshaler implementation."""

import logging
from collections import defaultdict

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.marshalers.relationships import (
    analyze_table_relationships as analyze_relationships,
)
from supabase_pydantic.db.marshalers.relationships import (
    determine_relationship_type as determine_rel_type,
)
from supabase_pydantic.db.models import ForeignKeyInfo, RelationshipInfo, TableInfo

# Get Logger
logger = logging.getLogger(__name__)


class MySQLRelationshipMarshaler(BaseRelationshipMarshaler):
    """MySQL relationship marshaler implementation."""

    def determine_relationship_type(
        self, source_table: TableInfo, target_table: TableInfo, source_column: str, target_column: str
    ) -> RelationType:
        """Determine the type of relationship between two tables.

        Args:
            source_table: Source table information.
            target_table: Target table information.
            source_column: Column name in source table.
            target_column: Column name in target table.

        Returns:
            RelationType enum value representing the relationship type.
        """
        # Create a meaningful constraint name based on tables and columns
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
        """Analyze relationships between tables.

        Args:
            tables: Dictionary of table information objects.
        """
        analyze_relationships(tables)

    def _determine_relationship_types(self, table_relationships: dict[str, list[RelationshipInfo]]) -> None:
        """Determine the relationship types based on foreign key constraints.

        This is a post-processing step that looks at all relationships to determine
        if they are one-to-one, one-to-many, or many-to-many.

        Args:
            table_relationships: Dictionary of table names to lists of RelationshipInfo objects
        """
        # First, collect information about foreign keys pointing to each table
        table_references = defaultdict(list)

        # For each table's relationships
        for table_name, relationships in table_relationships.items():
            for rel in relationships:
                # Record this relationship as pointing to the related table
                target_key = rel.related_table_name
                table_references[target_key].append((table_name, rel))

        # Now analyze the relationships to determine their types
        for table_name, relationships in table_relationships.items():
            for rel in relationships:
                # Check if other tables refer to this table
                references_to_this = table_references.get(table_name, [])

                if len(references_to_this) > 0:
                    # This is part of a bidirectional relationship

                    # Many-to-many: if this table refers to another table and that table also refers back
                    if any(ref_table == rel.related_table_name for ref_table, _ in references_to_this):
                        rel.relation_type = RelationType.MANY_TO_MANY
                    else:
                        # One-to-one or one-to-many, depending on constraints
                        # For simplicity in MySQL, assuming one-to-many as default
                        rel.relation_type = RelationType.ONE_TO_MANY
                else:
                    # This is a unidirectional relationship
                    # For MySQL, we default to many-to-one for unidirectional relationships
                    rel.relation_type = RelationType.MANY_TO_ONE
