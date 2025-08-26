"""Factory for creating connection parameter objects."""

from typing import Any

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import MySQLConnectionParams, PostgresConnectionParams
from supabase_pydantic.db.utils.url_parser import detect_database_type


class ConnectionParamFactory:
    """Factory for creating database connection parameter models."""

    @staticmethod
    def create_connection_params(
        conn_params: dict[str, Any], db_type: DatabaseType | None = None
    ) -> PostgresConnectionParams | MySQLConnectionParams:
        """Create connection parameter object based on database type.

        Args:
            conn_params: Dictionary of connection parameters
            db_type: Database type enum value, or None to auto-detect from DB_URL

        Returns:
            Connection parameter model instance

        Raises:
            ValueError: If database type cannot be determined or is not supported
        """
        # Auto-detect database type if not specified and db_url is available
        if db_type is None and conn_params.get('db_url'):
            detected_db_type = detect_database_type(conn_params['db_url'])
            if detected_db_type:
                db_type = detected_db_type

        # If still no db_type, default to PostgreSQL for backward compatibility
        if db_type is None:
            db_type = DatabaseType.POSTGRES

        # Create the appropriate connection parameter object
        if db_type == DatabaseType.POSTGRES:
            return PostgresConnectionParams(**conn_params)
        elif db_type == DatabaseType.MYSQL:
            return MySQLConnectionParams(**conn_params)
        else:
            raise ValueError(f'Unsupported database type: {db_type}')
