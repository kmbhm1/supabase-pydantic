"""Base adapter interface for database connections and schema introspection."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

# This will be moved to core models in a later refactoring
from src.supabase_pydantic.utils.dataclasses import TableInfo

# Type variable for the adapter implementation
T = TypeVar('T', bound='DatabaseAdapter')


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters.

    This class defines the interface that all database adapters must implement.
    Each database system (PostgreSQL, MySQL, SQLite, etc.) will have its own
    implementation of this interface.
    """

    @abstractmethod
    def __init__(self, **connection_params: Any) -> None:
        """Initialize the database adapter with connection parameters."""
        pass

    @abstractmethod
    def connect(self) -> Any:
        """Establish a connection to the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Check if the connection to the database is active."""
        pass

    @abstractmethod
    def query(self, query: str, params: tuple = ()) -> list[tuple]:
        """Execute a query against the database.

        Args:
            query: The SQL query to execute
            params: Optional parameters for the query

        Returns:
            A list of tuples containing the query results
        """
        pass

    @abstractmethod
    def get_schemas(self) -> list[str]:
        """Get a list of all non-system schemas in the database."""
        pass

    @abstractmethod
    def get_tables(self, schema: str) -> list[tuple]:
        """Get all tables and their columns for a given schema.

        Args:
            schema: The database schema to query

        Returns:
            A list of table information tuples
        """
        pass

    @abstractmethod
    def get_foreign_keys(self, schema: str) -> list[tuple]:
        """Get all foreign key relationships for a given schema.

        Args:
            schema: The database schema to query

        Returns:
            A list of foreign key relationship tuples
        """
        pass

    @abstractmethod
    def get_constraints(self, schema: str) -> list[tuple]:
        """Get all constraints for a given schema.

        Args:
            schema: The database schema to query

        Returns:
            A list of constraint tuples
        """
        pass

    @abstractmethod
    def get_user_defined_types(self, schema: str) -> list[tuple]:
        """Get all user-defined types for a given schema.

        Args:
            schema: The database schema to query

        Returns:
            A list of user-defined type tuples
        """
        pass

    @abstractmethod
    def type_map(self) -> dict[str, tuple[str, str | None]]:
        """Get the mapping of database types to Python/Pydantic types.

        Returns:
            A dictionary mapping database type names to (Python type, import statement) tuples
        """
        pass

    @abstractmethod
    def construct_table_info(self, schema: str = 'public') -> list[TableInfo]:
        """Construct TableInfo objects from database schema information.

        Args:
            schema: The database schema to use (default: 'public')

        Returns:
            A list of TableInfo objects representing the database schema
        """
        pass

    @classmethod
    def create_from_url(cls: type[T], db_url: str) -> T:
        """Create a database adapter from a connection URL.

        Args:
            db_url: The database connection URL

        Returns:
            An instance of the database adapter
        """
        raise NotImplementedError('This adapter does not support URL-based connections')

    def __enter__(self) -> Any:
        """Context manager entry point."""
        return self.connect()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Context manager exit point."""
        self.close()
        return False
