"""Database type enum for supported database backends."""

from enum import Enum


class DatabaseType(Enum):
    """Enum for supported database types."""

    POSTGRES = 'postgres'
    MYSQL = 'mysql'
    # Add other database types here as they are implemented
