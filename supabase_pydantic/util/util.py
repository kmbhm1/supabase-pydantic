from supabase_pydantic.util.constants import PYDANTIC_TYPE_MAP, SQLALCHEMY_TYPE_MAP


def adapt_type_map(
    postgres_type: str, default_type: tuple[str, str | None], type_map: dict[str, tuple[str, str | None]]
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
    postgres_type: str, default: tuple[str, str | None] = ('String', None)
) -> tuple[str, str | None]:
    """Get the SQLAlchemy type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, SQLALCHEMY_TYPE_MAP)


def get_pydantic_type(postgres_type: str, default: tuple[str, str | None] = ('Any', None)) -> tuple[str, str | None]:
    """Get the Pydantic type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, PYDANTIC_TYPE_MAP)
