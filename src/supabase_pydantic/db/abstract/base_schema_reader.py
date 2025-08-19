"""Abstract base schema reader for database introspection."""

from abc import ABC, abstractmethod
from typing import Any


class BaseSchemaReader(ABC):
    """Abstract base class for database schema introspection."""

    def __init__(self, connector: Any):
        """Initialize schema reader with a connector.

        Args:
            connector: Database connector instance.
        """
        self.connector = connector

    @abstractmethod
    def get_schemas(self, conn: Any) -> list[str]:
        """Get all schemas in the database.

        Args:
            conn: Database connection object.

        Returns:
            List of schema names.
        """
        pass

    @abstractmethod
    def get_tables(self, conn: Any, schema: str) -> list[tuple]:
        """Get all tables in the specified schema.

        Args:
            conn: Database connection object.
            schema: Schema name.

        Returns:
            List of table information as tuples.
        """
        pass

    @abstractmethod
    def get_columns(self, conn: Any, schema: str) -> list[tuple]:
        """Get all columns in the specified schema.

        Args:
            conn: Database connection object.
            schema: Schema name.

        Returns:
            List of column information as tuples.
        """
        pass

    @abstractmethod
    def get_foreign_keys(self, conn: Any, schema: str) -> list[tuple]:
        """Get all foreign keys in the specified schema.

        Args:
            conn: Database connection object.
            schema: Schema name.

        Returns:
            List of foreign key information as tuples.
        """
        pass

    @abstractmethod
    def get_constraints(self, conn: Any, schema: str) -> list[tuple]:
        """Get all constraints in the specified schema.

        Args:
            conn: Database connection object.
            schema: Schema name.

        Returns:
            List of constraint information as tuples.
        """
        pass

    @abstractmethod
    def get_user_defined_types(self, conn: Any, schema: str) -> list[tuple]:
        """Get all user-defined types in the specified schema.

        Args:
            conn: Database connection object.
            schema: Schema name.

        Returns:
            List of user-defined type information as tuples.
        """
        pass

    @abstractmethod
    def get_type_mappings(self, conn: Any, schema: str) -> list[tuple]:
        """Get type mapping information for the specified schema.

        Args:
            conn: Database connection object.
            schema: Schema name.

        Returns:
            List of type mapping information as tuples.
        """
        pass
