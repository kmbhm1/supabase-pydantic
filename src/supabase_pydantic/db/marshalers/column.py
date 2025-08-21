import builtins
import keyword
import logging

from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.type_factory import TypeMapFactory

# Get logger
logger = logging.getLogger(__name__)


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


def process_udt_field(udt_name: str, data_type: str, db_type: DatabaseType = DatabaseType.POSTGRES) -> str:
    """Process a user-defined type field.

    Args:
        udt_name: The user-defined type name
        data_type: The database data type
        db_type: The database type (used to select appropriate type maps)

    Returns:
        A string representing the Python/Pydantic type
    """
    logger.debug(f'Processing type: data_type={data_type}, udt_name={udt_name}, db_type={db_type}')

    pydantic_type: str

    # Select the appropriate type map based on the database type
    type_map: dict[str, tuple[str, str | None]]
    if db_type == DatabaseType.MYSQL:
        type_map = TypeMapFactory.get_pydantic_type_map(db_type)
    else:
        type_map = TypeMapFactory.get_pydantic_type_map(DatabaseType.POSTGRES)  # Default to PostgreSQL

    logger.debug(f'Using type map: {list(type_map.keys())[:5]}... (showing first 5 keys)')

    # First, check if this is an array type
    if data_type.lower() == 'array' or data_type.lower().endswith('[]'):
        # Extract the element type name
        element_type_name = udt_name.strip('_').lower()

        # Simplified approach: check if the element type exists in the type map
        element_mapping = type_map.get(element_type_name)
        if element_mapping:
            element_pydantic_type = element_mapping[0]
            logger.debug(f'Found array element type mapping for {element_type_name}: {element_pydantic_type}')
        else:
            # Default to Any for unknown types
            element_pydantic_type = 'Any'
            logger.warning(f'Unknown array element type: {element_type_name}, using Any')

        # Create a properly typed list
        pydantic_type = f'list[{element_pydantic_type}]'
    else:
        # Regular non-array type
        # Convert data_type to lowercase for case-insensitive matching
        data_type_lower = data_type.lower()

        # Try to find the type in the type map
        type_mapping = type_map.get(data_type_lower)

        if type_mapping:
            pydantic_type = type_mapping[0]
            logger.debug(f'Found type mapping for {data_type_lower}: {pydantic_type}')
        else:
            # No match found in the type map, default to Any
            pydantic_type = 'Any'
            logger.warning(
                f'No type mapping found for {data_type_lower}, using Any. Available keys: {list(type_map.keys())[:10]}'
            )

    return pydantic_type
