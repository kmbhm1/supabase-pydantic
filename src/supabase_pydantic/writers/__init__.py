from src.supabase_pydantic.core.constants import OrmType
from src.supabase_pydantic.core.formatters import write_model_file
from src.supabase_pydantic.utils.dataclasses import TableInfo

from .factories import FileWriterFactory
from .pydantic_writers import PydanticFastAPIWriter
from .sqlalchemy_writers import SqlAlchemyFastAPIWriter
from .util import generate_unique_filename, write_seed_file

__all__ = [
    'FileWriterFactory',
    'generate_unique_filename',
    'output_pydantic',
    'output_sqlalchemy',
    'write_seed_file',
]


def output_pydantic(
    tables: list[TableInfo],
    output_directory: str,
    filename: str | None = None,
    add_null_parent_classes: bool = False,
    generate_crud_models: bool = True,
    generate_enums: bool = True,
) -> str:
    """Generate Pydantic models from table definitions and write them to a file.

    Args:
        tables: List of TableInfo objects containing database table information
        output_directory: Directory where the model file will be written
        filename: Optional custom filename (will use default if not provided)
        add_null_parent_classes: Whether to generate parent classes with nullable fields
        generate_crud_models: Whether to generate Insert and Update models
        generate_enums: Whether to generate enum types

    Returns:
        Path to the generated file
    """
    writer = PydanticFastAPIWriter(
        tables,
        '',  # We don't use the file_path in this context
        add_null_parent_classes=add_null_parent_classes,
        generate_crud_models=generate_crud_models,
        generate_enums=generate_enums,
    )
    code = writer.write()
    return write_model_file(code, output_directory, OrmType.PYDANTIC, filename)


def output_sqlalchemy(
    tables: list[TableInfo],
    output_directory: str,
    filename: str | None = None,
    add_null_parent_classes: bool = False,
) -> str:
    """Generate SQLAlchemy models from table definitions and write them to a file.

    Args:
        tables: List of TableInfo objects containing database table information
        output_directory: Directory where the model file will be written
        filename: Optional custom filename (will use default if not provided)
        add_null_parent_classes: Whether to generate parent classes with nullable fields

    Returns:
        Path to the generated file
    """
    writer = SqlAlchemyFastAPIWriter(
        tables,
        '',  # We don't use the file_path in this context
        add_null_parent_classes=add_null_parent_classes,
    )
    code = writer.write()
    return write_model_file(code, output_directory, OrmType.SQLALCHEMY, filename)
