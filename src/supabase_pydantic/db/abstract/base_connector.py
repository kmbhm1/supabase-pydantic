"""Abstract base connector for database operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel

from supabase_pydantic.db.models import DatabaseConnectionParams

T = TypeVar('T', bound=DatabaseConnectionParams)


class BaseDBConnector(ABC, Generic[T]):
    """Abstract base class for database connectors."""

    params_model: T | None  # Type annotation to indicate params_model can be None
    connection_params: dict[str, Any]
    connection: Any | None

    def __init__(self, connection_params: T | dict[str, Any] | None = None, **kwargs: Any):
        """Initialize the connector with connection parameters.

        Args:
            connection_params: Connection parameters as a Pydantic model or dict
            **kwargs: Additional connection parameters to store for later use
        """
        self.connection = None

        # If a Pydantic model is provided, use it
        if isinstance(connection_params, BaseModel):
            self.params_model = connection_params  # type: ignore
            # Handle both custom to_dict method and standard Pydantic model_dump
            if hasattr(connection_params, 'to_dict'):
                self.connection_params = connection_params.to_dict()
            else:
                self.connection_params = connection_params.model_dump()
        # If a dict is provided, use it directly
        elif isinstance(connection_params, dict):
            self.params_model = None
            self.connection_params = connection_params
        # If kwargs are provided, use them
        else:
            self.params_model = None
            self.connection_params = kwargs

    @abstractmethod
    def connect(self, connection_params: T | dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Create a connection to the database.

        Args:
            connection_params: Connection parameters as a Pydantic model or dict
            **kwargs: Additional connection parameters specific to the database.
                May include db_url, dbname, user, password, host, port, etc.

        Returns:
            A database connection object specific to the database implementation.

        Raises:
            ConnectionError: If connection to the database fails.
        """
        pass

    @abstractmethod
    def check_connection(self, conn: Any) -> bool:
        """Check if connection is active.

        Args:
            conn: Database connection object.

        Returns:
            True if connection is active, False otherwise.
        """
        pass

    @abstractmethod
    def validate_connection_params(self, params: T | dict[str, Any]) -> T:
        """Validate and convert connection parameters to the appropriate Pydantic model.

        Args:
            params: Connection parameters as a Pydantic model or dict

        Returns:
            Validated connection parameters as a Pydantic model

        Raises:
            ValueError: If connection parameters are invalid
        """
        pass

    @abstractmethod
    def execute_query(self, conn: Any, query: str, params: tuple = ()) -> list[tuple]:
        """Execute a query and return results.

        Args:
            conn: Database connection object.
            query: SQL query to execute.
            params: Parameters for the SQL query.

        Returns:
            List of result rows as tuples.
        """
        pass

    @abstractmethod
    def close_connection(self, conn: Any) -> None:
        """Close the database connection.

        Args:
            conn: Database connection object.
        """
        pass

    @abstractmethod
    def get_url_connection_params(self, url: str) -> dict[str, Any]:
        """Parse connection URL into parameters.

        Args:
            url: Database connection URL.

        Returns:
            Dictionary of connection parameters.

        Raises:
            ValueError: If URL is invalid or cannot be parsed.
        """
        pass

    def __enter__(self) -> Any:
        """Context manager entry.

        Returns:
            Database connection object.
        """
        if self.params_model:
            self.connection = self.connect(self.params_model)  # type: ignore
        else:
            self.connection = self.connect(self.connection_params)
        return self.connection

    def __exit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> Literal[False]:
        """Context manager exit.

        Args:
            exc_type: Exception type.
            exc_val: Exception value.
            exc_tb: Exception traceback.

        Returns:
            False to propagate exceptions.
        """
        self.close_connection(self.connection)
        return False
