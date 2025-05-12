"""Utility functions for type handling and conversion."""

from typing import Any

from src.supabase_pydantic.core.constants import PYDANTIC_TYPE_MAP, SQLALCHEMY_TYPE_MAP, RelationType


def to_pascal_case(string: str) -> str:
    """Converts a string to PascalCase."""
    words = string.split('_')
    camel_case = ''.join(word.capitalize() for word in words)
    return camel_case


def chunk_text(text: str, nchars: int = 79) -> list[str]:
    """Split text into lines with a maximum number of characters."""
    words = text.split()  # Split the text into words
    lines: list[str] = []  # This will store the final lines
    current_line: list[str] = []  # This will store words for the current line

    for word in words:
        # Check if adding the next word would exceed the length limit
        if (sum(len(w) for w in current_line) + len(word) + len(current_line)) > nchars:
            # If adding the word would exceed the limit, join current_line into a string and add to lines
            lines.append(' '.join(current_line))
            current_line = [word]  # Start a new line with the current word
        else:
            current_line.append(word)  # Add the word to the current line

    # Add the last line to lines if any words are left unadded
    if current_line:
        lines.append(' '.join(current_line))

    return lines


def get_enum_member_from_string(cls: Any, value: str) -> Any:
    """Get an Enum member from a string value."""
    value_lower = value.lower()
    for member in cls:
        if member.value == value_lower:
            return member
    raise ValueError(f"'{value}' is not a valid {cls.__name__}")


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


def get_pydantic_type(postgres_type: str, default: tuple[str, str | None] = ('Any', None)) -> tuple[str, str | None]:
    """Get the Pydantic type from the PostgreSQL type."""
    return adapt_type_map(postgres_type, default, PYDANTIC_TYPE_MAP)


def get_relationship_field_type(relation_type: RelationType | None, class_name: str) -> str:
    """Get the appropriate field type based on the relationship type.

    This function is crucial for generating correct type annotations in Pydantic models
    based on the detected relationship type.

    Args:
        relation_type: The detected relationship type
        class_name: The name of the related class/model

    Returns:
        A string with the appropriate type annotation
    """
    if relation_type == RelationType.ONE_TO_ONE or relation_type == RelationType.MANY_TO_ONE:
        # For one-to-one and many-to-one relationships, we use a single instance
        return f'{class_name} | None'
    else:
        # For one-to-many and many-to-many relationships, we use a list
        return f'list[{class_name}] | None'
