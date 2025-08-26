from typing import Any

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.type_factory import TypeMapFactory

# enum helpers


def get_enum_member_from_string(cls: Any, value: str) -> Any:
    """Get an Enum member from a string value."""
    value_lower = value.lower()
    for member in cls:
        if member.value == value_lower:
            return member
    raise ValueError(f"'{value}' is not a valid {cls.__name__}")


# type map helpers


def adapt_type_map(
    db_type: str,
    default_type: tuple[str, str | None],
    type_map: dict[str, tuple[str, str | None]],
) -> tuple[str, str | None]:
    """Adapt a database data type to a Pydantic and SQLAlchemy type."""
    array_suffix = '[]'
    if db_type.endswith(array_suffix):
        base_type = db_type[: -len(array_suffix)]
        sqlalchemy_type, import_statement = type_map.get(base_type, default_type)
        adapted_type = f'ARRAY({sqlalchemy_type})'
        import_statement = (
            f'{import_statement}, ARRAY' if import_statement else 'from sqlalchemy.dialects.postgresql import ARRAY'
        )
    else:
        adapted_type, import_statement = type_map.get(db_type, default_type)

    return (adapted_type, import_statement)


def get_sqlalchemy_type(
    db_type: str,
    database_type: DatabaseType = DatabaseType.POSTGRES,
    default: tuple[str, str | None] = ('String', 'from sqlalchemy import String'),
) -> tuple[str, str | None]:
    """Get the SQLAlchemy type from the database type."""
    type_map = TypeMapFactory.get_sqlalchemy_type_map(database_type)
    return adapt_type_map(db_type, default, type_map)


def get_sqlalchemy_v2_type(
    db_type: str,
    database_type: DatabaseType = DatabaseType.POSTGRES,
    default: tuple[str, str | None] = ('String,str', 'from sqlalchemy import String'),
) -> tuple[str, str, str | None]:
    """Get the SQLAlchemy v2 type from the database type."""
    type_map = TypeMapFactory.get_sqlalchemy_v2_type_map(database_type)
    both_types, imports = adapt_type_map(db_type, default, type_map)
    sql, py = both_types.split(',')
    # print(f'get_sqlalchemy_v2_type({db_type}, {database_type}, {default}) -> ({sql}, {py}, {imports})')
    return (sql, py, imports)


def get_pydantic_type(
    db_type: str,
    database_type: DatabaseType = DatabaseType.POSTGRES,
    default: tuple[str, str | None] = ('Any', 'from typing import Any'),
) -> tuple[str, str | None]:
    """Get the Pydantic type from the database type."""
    type_map = TypeMapFactory.get_pydantic_type_map(database_type)
    return adapt_type_map(db_type, default, type_map)
