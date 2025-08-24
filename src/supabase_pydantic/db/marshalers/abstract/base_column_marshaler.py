"""Abstract base class for column marshaling."""

from abc import ABC, abstractmethod


class BaseColumnMarshaler(ABC):
    """Abstract base class for column data marshaling."""

    @abstractmethod
    def standardize_column_name(self, column_name: str, disable_model_prefix_protection: bool = False) -> str:
        """Standardize column names across database types.

        Args:
            column_name: Raw column name from database.
            disable_model_prefix_protection: Whether to disable model prefix protection.

        Returns:
            Standardized column name suitable for Python code.
        """
        pass

    @abstractmethod
    def get_alias(self, column_name: str) -> str:
        """Get alias for a column name.

        Args:
            column_name: Raw column name from database.

        Returns:
            Aliased column name if needed.
        """
        pass

    @abstractmethod
    def process_column_type(self, db_type: str, type_info: str, enum_types: list[str] | None = None) -> str:
        """Process database-specific column type into standard Python type.

        Args:
            db_type: Database-specific type name.
            type_info: Additional type information.
            enum_types: Optional list of known enum type names.

        Returns:
            Python/Pydantic type name.
        """
        pass

    @abstractmethod
    def process_array_type(self, element_type: str) -> str:
        """Process array types for the database.

        Args:
            element_type: Type of array elements.

        Returns:
            Python representation of array type.
        """
        pass
