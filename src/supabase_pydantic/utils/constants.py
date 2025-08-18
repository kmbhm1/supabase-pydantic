from typing import TypedDict


class AppConfig(TypedDict, total=False):
    """Configuration for the Supabase Pydantic tool."""

    default_directory: str
    overwrite_existing_files: bool
    nullify_base_schema: bool
    disable_model_prefix_protection: bool


class ToolConfig(TypedDict):
    """Configuration for the Supabase Pydantic tool."""

    supabase_pydantic: AppConfig


# File Names
STD_PYDANTIC_FILENAME = 'schemas.py'
STD_SQLALCHEMY_FILENAME = 'database.py'
STD_SEED_DATA_FILENAME = 'seed.sql'
