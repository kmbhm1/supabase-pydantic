"""URL parser utilities for database connections."""

import re

from supabase_pydantic.db.database_type import DatabaseType

# Connection string regexes for different database types
POSTGRES_CONN_REGEX = (
    r'(postgresql|postgres)://([^:@\s]*(?::[^@\s]*)?@)?(?P<server>[^/\?\s:]+)(:\d+)?(/[^?\s]*)?(\?[^\s]*)?$'
)
MYSQL_CONN_REGEX = r'(mysql|mariadb)://([^:@\s]*(?::[^@\s]*)?@)?(?P<server>[^/\?\s:]+)(:\d+)?(/[^?\s]*)?(\?[^\s]*)?$'


def detect_database_type(db_url: str) -> DatabaseType | None:
    """Detect the database type from a connection URL.

    Args:
        db_url: Database connection URL

    Returns:
        DatabaseType enum value or None if unknown
    """
    if not db_url:
        return None

    if re.match(POSTGRES_CONN_REGEX, db_url):
        return DatabaseType.POSTGRES
    elif re.match(MYSQL_CONN_REGEX, db_url):
        return DatabaseType.MYSQL

    return None


def get_database_name_from_url(db_url: str) -> str | None:
    """Extract database name from connection URL.

    Args:
        db_url: Database connection URL

    Returns:
        Database name or None if not found
    """
    if not db_url:
        return None

    # Extract the path component
    path_match = re.search(r'://[^/]+/([^?]+)', db_url)
    if path_match:
        return path_match.group(1)

    return None
