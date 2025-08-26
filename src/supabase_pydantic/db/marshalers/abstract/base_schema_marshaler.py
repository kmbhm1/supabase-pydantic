"""Abstract base class for schema marshaling."""

from abc import ABC, abstractmethod

from supabase_pydantic.db.marshalers.abstract.base_column_marshaler import BaseColumnMarshaler
from supabase_pydantic.db.marshalers.abstract.base_constraint_marshaler import BaseConstraintMarshaler
from supabase_pydantic.db.marshalers.abstract.base_relationship_marshaler import BaseRelationshipMarshaler
from supabase_pydantic.db.models import TableInfo


class BaseSchemaMarshaler(ABC):
    """Abstract base class for database schema marshaling."""

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
        self.column_marshaler = column_marshaler
        self.constraint_marshaler = constraint_marshaler
        self.relationship_marshaler = relationship_marshaler

    @abstractmethod
    def get_table_details_from_columns(self, column_data: list[tuple]) -> dict[tuple[str, str], TableInfo]:
        """Process database-specific column data into TableInfo objects.

        Args:
            column_data: Raw column data from database.

        Returns:
            Dictionary mapping (schema, table) tuples to TableInfo objects.
        """
        pass

    @abstractmethod
    def process_foreign_keys(self, tables: dict[tuple[str, str], TableInfo], fk_data: list[tuple]) -> None:
        """Add foreign key information to tables.

        Args:
            tables: Dictionary of table information objects.
            fk_data: Raw foreign key data from database.
        """
        pass

    @abstractmethod
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
        """Construct TableInfo objects from database-specific data.

        Args:
            table_data: Raw table data from database.
            column_data: Raw column data from database.
            fk_data: Raw foreign key data from database.
            constraint_data: Raw constraint data from database.
            type_data: Raw user-defined type data from database.
            type_mapping_data: Raw type mapping data from database.
            schema: Schema name.
            disable_model_prefix_protection: Whether to disable model prefix protection.

        Returns:
            List of TableInfo objects.
        """
        pass
