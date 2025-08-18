import builtins
import keyword

from supabase_pydantic.core.constants import PYDANTIC_TYPE_MAP


def string_is_reserved(value: str) -> bool:
    """Check if the string is a reserved keyword or built-in name."""
    return value in dir(builtins) or value in keyword.kwlist


def column_name_is_reserved(column_name: str, disable_model_prefix_protection: bool = False) -> bool:
    """Check if the column name is a reserved keyword or built-in name or starts with model_.

    If disable_model_prefix_protection is True, only check for reserved keywords, not model_ prefix.
    """
    if disable_model_prefix_protection:
        # Only check if it's a reserved keyword, ignore model_ prefix
        return string_is_reserved(column_name)
    else:
        # Check both reserved keywords and model_ prefix (original behavior)
        return string_is_reserved(column_name) or column_name.startswith('model_')


def column_name_reserved_exceptions(column_name: str) -> bool:
    """Check for select exceptions to the reserved column name check."""
    exceptions = ['id', 'credits', 'copyright', 'license', 'help', 'property', 'sum']
    return column_name.lower() in exceptions


def standardize_column_name(column_name: str, disable_model_prefix_protection: bool = False) -> str | None:
    """Check if the column name is a reserved keyword or built-in name and replace it if necessary.

    If disable_model_prefix_protection is True, only process reserved keywords, not model_ prefix.
    """
    return (
        f'field_{column_name}'
        if column_name_is_reserved(column_name, disable_model_prefix_protection)
        and not column_name_reserved_exceptions(column_name)
        else column_name
    )


def get_alias(column_name: str, disable_model_prefix_protection: bool = False) -> str | None:
    """Provide the original column name as an alias for Pydantic.

    If disable_model_prefix_protection is True, don't create aliases for model_ prefixed columns.
    """
    return (
        column_name
        if column_name_is_reserved(column_name, disable_model_prefix_protection)
        and not column_name_reserved_exceptions(column_name)
        else None
    )


def process_udt_field(udt_name: str, data_type: str) -> str:
    """Process a user-defined type field."""
    pydantic_type: str
    is_array = udt_name.startswith('_')

    if is_array:  # This is an array type
        # Extract the element type by removing the underscore
        element_type_name = udt_name[1:]

        # Map the PostgreSQL element type to a Pydantic type
        # First, try to find a direct mapping for the element type
        element_type_mapping = PYDANTIC_TYPE_MAP.get(element_type_name)
        if element_type_mapping:
            element_pydantic_type = element_type_mapping[0]
        else:
            # Fall back to a heuristic mapping based on common types
            if element_type_name in ('text', 'varchar', 'char', 'bpchar', 'name'):
                element_pydantic_type = 'str'
            elif element_type_name in ('int2', 'int4', 'int8', 'serial2', 'serial4', 'serial8'):
                element_pydantic_type = 'int'
            elif element_type_name in ('float4', 'float8', 'numeric', 'decimal'):
                element_pydantic_type = 'float'
            elif element_type_name == 'bool':
                element_pydantic_type = 'bool'
            elif element_type_name == 'uuid':
                element_pydantic_type = 'UUID'
            elif element_type_name in ('timestamp', 'timestamptz', 'date', 'time', 'timetz'):
                element_pydantic_type = 'datetime'
            elif element_type_name == 'json' or element_type_name == 'jsonb':
                element_pydantic_type = 'dict'
            else:
                # For custom types like enums, use a temporary 'Any' type
                # We'll properly handle this with enum_info later
                element_pydantic_type = 'Any'

        # Create a properly typed list
        pydantic_type = f'list[{element_pydantic_type}]'
    else:
        # Regular non-array type
        pydantic_type = PYDANTIC_TYPE_MAP.get(data_type, ('Any', 'from typing import Any'))[0]

    return pydantic_type
