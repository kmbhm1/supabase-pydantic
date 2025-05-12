"""Database adapter module for multiple database systems."""

from enum import Enum, auto
from typing import Any

from .base import DatabaseAdapter
from .postgres import PostgresAdapter


class DatabaseType(Enum):
    """Supported database systems."""

    POSTGRES = auto()
    # Future database types will be added here
    # MYSQL = auto()
    # SQLITE = auto()
    # SQLSERVER = auto()


class AdapterFactory:
    """Factory for creating database adapters."""

    @staticmethod
    def create_adapter(db_type: DatabaseType, **connection_params: Any) -> DatabaseAdapter:
        """Create a database adapter for the specified database type.

        Args:
            db_type: The type of database to connect to
            **connection_params: Connection parameters for the database

        Returns:
            A database adapter instance

        Raises:
            ValueError: If the database type is not supported
        """
        adapters = {
            DatabaseType.POSTGRES: PostgresAdapter,
            # Add more adapters as they are implemented
        }

        adapter_class = adapters.get(db_type)
        if not adapter_class:
            supported = ', '.join(t.name for t in adapters.keys())
            raise ValueError(f'Unsupported database type: {db_type}. Supported types: {supported}')

        return adapter_class(**connection_params)

    @staticmethod
    def create_from_url(url: str) -> DatabaseAdapter:
        """Create a database adapter from a connection URL.

        The database type is inferred from the URL scheme.

        Args:
            url: Database connection URL (e.g., postgresql://user:pass@host:port/db)

        Returns:
            A database adapter instance

        Raises:
            ValueError: If the database type could not be determined or is not supported
        """
        if url.startswith(('postgresql://', 'postgres://')):
            return PostgresAdapter.create_from_url(url)

        # Add more URL scheme handlers as more database types are supported

        raise ValueError(f'Unsupported database URL scheme: {url}')


__all__ = ['DatabaseAdapter', 'PostgresAdapter', 'DatabaseType', 'AdapterFactory']
