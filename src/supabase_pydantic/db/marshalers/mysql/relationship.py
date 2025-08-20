"""MySQL relationship marshaler implementation."""

import logging
from collections import defaultdict
from typing import Any

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.marshalers.relationships import (
    analyze_table_relationships as analyze_relationships,
)
from supabase_pydantic.db.marshalers.relationships import (
    determine_relationship_type as determine_rel_type,
)
from supabase_pydantic.db.models import ForeignKeyInfo, RelationshipInfo, TableInfo
from supabase_pydantic.utils.strings import to_pascal_case

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

    def marshal(self, data: list[dict[str, Any]], schema: str, **kwargs: Any) -> dict[str, list[RelationshipInfo]]:
        """Marshal foreign key data into RelationshipInfo objects.

        Args:
            data: Raw foreign key data from the database
            schema: Schema name
            **kwargs: Additional arguments

        Returns:
            Dictionary of table names to lists of RelationshipInfo objects
        """
        if not data:
            logger.warning(f'No relationship data to marshal for schema {schema}')
            return {}

        # Group foreign keys by table
        table_relationships: dict[str, list[RelationshipInfo]] = {}
        processed_relations: set[str] = set()  # Track processed relationships to avoid duplicates

        for relation in data:
            table_name = relation.get('table_name', '')
            constraint_name = relation.get('constraint_name', '')
            column_name = relation.get('column_name', '')
            foreign_table_name = relation.get('foreign_table_name', '')
            foreign_column_name = relation.get('foreign_column_name', '')

            # Skip if missing essential data
            if not table_name or not column_name or not foreign_table_name or not foreign_column_name:
                logger.warning(f'Relationship data missing required fields: {relation}')
                continue

            # Skip if already processed this relationship
            relation_key = f'{table_name}:{column_name}:{foreign_table_name}:{foreign_column_name}'
            if relation_key in processed_relations:
                continue
            processed_relations.add(relation_key)

            # Determine relationship type
            # By default, assume one-to-many: one row in foreign table can have many rows in this table
            rel_type = RelationType.MANY_TO_ONE

            # Create relationship info
            relationship_info = RelationshipInfo(
                constraint_name=constraint_name,
                table=table_name,
                column=column_name,
                foreign_table=foreign_table_name,
                foreign_column=foreign_column_name,
                type=rel_type,
                # Convert snake_case to PascalCase for class names
                foreign_table_class=to_pascal_case(foreign_table_name),
                update_rule=relation.get('update_rule', ''),
                delete_rule=relation.get('delete_rule', ''),
            )

            # Add to table relationships
            if table_name not in table_relationships:
                table_relationships[table_name] = []
            table_relationships[table_name].append(relationship_info)

        # Post-process to determine actual relationship types
        self._determine_relationship_types(table_relationships)

        return table_relationships

    def _determine_relationship_types(self, table_relationships: dict[str, list[RelationshipInfo]]) -> None:
        """Determine the relationship types based on foreign key constraints.

        This is a post-processing step that looks at all relationships to determine
        if they are one-to-one, one-to-many, or many-to-many.

        Args:
            table_relationships: Dictionary of table names to lists of RelationshipInfo objects
        """
        # First, collect information about foreign keys pointing to each table/column
        table_column_references = defaultdict(list)

        # For each table's relationships
        for table_name, relationships in table_relationships.items():
            for rel in relationships:
                # Record this relationship as pointing to the foreign table/column
                target_key = (rel.foreign_table, rel.foreign_column)
                table_column_references[target_key].append((table_name, rel))

        # Now analyze the relationships to determine their types
        for table_name, relationships in table_relationships.items():
            for rel in relationships:
                # The key for this table's column that others might refer to
                this_key = (table_name, rel.column)

                # Check if other tables refer to this column
                references_to_this = table_column_references.get(this_key, [])

                if len(references_to_this) > 0:
                    # This is part of a bidirectional relationship

                    # Many-to-many: if this table refers to another table and that table also refers back
                    if any(ref_table == rel.foreign_table for ref_table, _ in references_to_this):
                        rel.type = RelationType.MANY_TO_MANY
                    else:
                        # One-to-one or one-to-many, depending on constraints
                        # For simplicity in MySQL, assuming one-to-many as default
                        rel.type = RelationType.ONE_TO_MANY
                else:
                    # This is a unidirectional relationship
                    # For MySQL, we default to many-to-one for unidirectional relationships
                    rel.type = RelationType.MANY_TO_ONE
