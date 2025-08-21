"""Factory for database-specific type maps."""

from typing import cast

from supabase_pydantic.core.constants import PYDANTIC_TYPE_MAP, SQLALCHEMY_TYPE_MAP, SQLALCHEMY_V2_TYPE_MAP
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.drivers.mysql.type_maps import (
    MYSQL_PYDANTIC_TYPE_MAP,
    MYSQL_SQLALCHEMY_TYPE_MAP,
    MYSQL_SQLALCHEMY_V2_TYPE_MAP,
)

# Type annotations for imported maps
PydanticTypeMap = dict[str, tuple[str, str | None]]
SQLAlchemyTypeMap = dict[str, tuple[str, str | None]]
SQLAlchemyV2TypeMap = dict[str, tuple[str, str | None]]


class TypeMapFactory:
    """Factory for database-specific type maps."""

    @staticmethod
    def get_pydantic_type_map(db_type: DatabaseType) -> dict[str, tuple[str, str | None]]:
        """Get the Pydantic type map for a specific database type."""
        if db_type == DatabaseType.MYSQL:
            return cast(PydanticTypeMap, MYSQL_PYDANTIC_TYPE_MAP)
        # Default to PostgreSQL
        return cast(PydanticTypeMap, PYDANTIC_TYPE_MAP)

    @staticmethod
    def get_sqlalchemy_type_map(db_type: DatabaseType) -> dict[str, tuple[str, str | None]]:
        """Get the SQLAlchemy type map for a specific database type."""
        if db_type == DatabaseType.MYSQL:
            return cast(SQLAlchemyTypeMap, MYSQL_SQLALCHEMY_TYPE_MAP)
        # Default to PostgreSQL
        return cast(SQLAlchemyTypeMap, SQLALCHEMY_TYPE_MAP)

    @staticmethod
    def get_sqlalchemy_v2_type_map(db_type: DatabaseType) -> dict[str, tuple[str, str | None]]:
        """Get the SQLAlchemy V2 type map for a specific database type."""
        if db_type == DatabaseType.MYSQL:
            return cast(SQLAlchemyV2TypeMap, MYSQL_SQLALCHEMY_V2_TYPE_MAP)
        # Default to PostgreSQL
        return cast(SQLAlchemyV2TypeMap, SQLALCHEMY_V2_TYPE_MAP)
