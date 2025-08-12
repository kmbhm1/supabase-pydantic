from typing import Any

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
    postgres_type: str,
    default_type: tuple[str, str | None],
    type_map: dict[str, tuple[str, str | None]],
) -> tuple[str, str | None]:
    """Adapt a PostgreSQL data type to a Pydantic and SQLAlchemy type."""
    array_suffix = '[]'
    if postgres_type.endswith(array_suffix):
        base_type = postgres_type[: -len(array_suffix)]
        sqlalchemy_type, import_statement = type_map.get(base_type, default_type)
        adapted_type = f'ARRAY({sqlalchemy_type})'
        import_statement = (
            f'{import_statement}, ARRAY' if import_statement else 'from sqlalchemy.dialects.postgresql import ARRAY'
        )
    else:
        adapted_type, import_statement = type_map.get(postgres_type, default_type)

    return (adapted_type, import_statement)


def get_sqlalchemy_type(
    postgres_type: str, default: tuple[str, str | None] = ('String', 'from sqlalchemy import String')
) -> tuple[str, str | None]:
    """Get the SQLAlchemy type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, SQLALCHEMY_TYPE_MAP)


def get_sqlalchemy_v2_type(
    postgres_type: str, default: tuple[str, str | None] = ('String,str', 'from sqlalchemy import String')
) -> tuple[str, str, str | None]:
    """Get the SQLAlchemy v2 type from the PostgreSQL type."""
    both_types, imports = adapt_type_map(postgres_type, default, SQLALCHEMY_V2_TYPE_MAP)
    sql, py = both_types.split(',')
    return (sql, py, imports)


def get_pydantic_type(postgres_type: str, default: tuple[str, str | None] = ('Any', None)) -> tuple[str, str | None]:
    """Get the Pydantic type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, PYDANTIC_TYPE_MAP)
