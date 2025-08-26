"""Abstract base class for relationship marshaling."""

from abc import ABC, abstractmethod

from supabase_pydantic.db.constants import RelationType
from supabase_pydantic.db.models import TableInfo


class BaseRelationshipMarshaler(ABC):
    """Abstract base class for relationship data marshaling."""

    @abstractmethod
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
        pass

    @abstractmethod
    def analyze_table_relationships(self, tables: dict[tuple[str, str], TableInfo]) -> None:
        """Analyze relationships between tables.

        Args:
            tables: Dictionary of table information objects.
        """
        pass
