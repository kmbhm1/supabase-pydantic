from enum import Enum


class RelationType(str, Enum):
    """Enum for relation types."""

    ONE_TO_ONE = 'One-to-One'
    ONE_TO_MANY = 'One-to-Many'
    MANY_TO_MANY = 'Many-to-Many'
    MANY_TO_ONE = 'Many-to-One'  # When a table has a foreign key to another table (e.g., File -> Project)


class DatabaseConnectionType(Enum):
    """Enum for database connection types."""

    LOCAL = 'local'
    DB_URL = 'db_url'


class DatabaseUserDefinedType(str, Enum):
    """Enum for database user defined types."""

    DOMAIN = 'DOMAIN'
    COMPOSITE = 'COMPOSITE'
    ENUM = 'ENUM'
    RANGE = 'RANGE'


# Regex

POSTGRES_SQL_CONN_REGEX = (
    r'(postgresql|postgres)://([^:@\s]*(?::[^@\s]*)?@)?(?P<server>[^/\?\s:]+)(:\d+)?(/[^?\s]*)?(\?[^\s]*)?$'
)
