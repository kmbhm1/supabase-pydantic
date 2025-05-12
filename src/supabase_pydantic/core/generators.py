"""Model generation utilities for supabase-pydantic.

This module contains functions to generate Pydantic and SQLAlchemy models
from database schema information.
"""

import logging
import re

from src.supabase_pydantic.core.constants import (
    BASE_CLASS_POSTFIX,
    OrmType,
    RelationType,
    WriterClassType,
)
from src.supabase_pydantic.core.models import ColumnInfo, TableInfo
from src.supabase_pydantic.core.type_utils import get_relationship_field_type, to_pascal_case


def clean_name_for_identifier(name: str) -> str:
    """Remove or replace characters that are not valid for Python identifiers."""
    # Replace spaces, hyphens, and other non-alphanumeric characters with underscores
    cleaned = re.sub(r'[^\w]', '_', name)
    # Ensure the name doesn't start with a digit
    if cleaned and cleaned[0].isdigit():
        cleaned = f'_{cleaned}'
    return cleaned


def generate_pydantic_model_name(table_name: str, class_type: WriterClassType) -> str:
    """Generate a Pydantic model name for a table."""
    pascal_name = to_pascal_case(table_name)

    if class_type == WriterClassType.BASE:
        return f'{pascal_name}{BASE_CLASS_POSTFIX}'
    elif class_type == WriterClassType.BASE_WITH_PARENT:
        return f'{pascal_name}WithParent'
    elif class_type == WriterClassType.PARENT:
        return f'{pascal_name}Parent'
    elif class_type == WriterClassType.INSERT:
        return f'{pascal_name}Insert'
    elif class_type == WriterClassType.UPDATE:
        return f'{pascal_name}Update'

    return pascal_name


def get_column_type_annotation(column: ColumnInfo) -> str:
    """Get the type annotation for a column based on its properties."""
    base_type = column.datatype

    # Handle nullability
    if column.is_nullable:
        return f'{base_type} | None'
    return base_type


def get_required_imports(tables: list[TableInfo]) -> set[str]:
    """Get the set of required imports for the generated models."""
    imports = {
        'from pydantic import BaseModel, Field',
        'from typing import Optional, List',
    }

    for table in tables:
        for column in table.columns:
            # Add any special imports from column datatypes
            datatype_parts = column.datatype.split('.')
            if len(datatype_parts) > 1:
                module = '.'.join(datatype_parts[:-1])
                imports.add(f'import {module}')

            # Check for enum imports
            if column.user_enum_type:
                imports.add('from enum import Enum')

    return imports


def generate_enum_classes(tables: list[TableInfo]) -> str:
    """Generate enum classes for user-defined enum types."""
    enums_code = []

    # Track processed enums to avoid duplicates
    processed_enums = set()

    for table in tables:
        for column in table.columns:
            enum_type = column.user_enum_type
            if enum_type and enum_type.name not in processed_enums:
                processed_enums.add(enum_type.name)

                enum_name = to_pascal_case(enum_type.name)
                enum_values = [f"    {clean_name_for_identifier(value)} = '{value}'" for value in enum_type.values]

                enum_code = [
                    f'class {enum_name}(str, Enum):',
                    *enum_values,
                    '',  # Empty line after the enum
                ]

                enums_code.extend(enum_code)

    return '\n'.join(enums_code)


def generate_relationship_fields(
    table: TableInfo, tables: dict[str, TableInfo], model_type: WriterClassType
) -> list[str]:
    """
    Generate Pydantic model fields for relationships based on relationship types.

    This function is key to generating the correct field types for different relationship types.
    """
    relationship_fields = []

    # Skip relationships for certain model types
    if model_type in [WriterClassType.INSERT, WriterClassType.UPDATE]:
        return []

    for fk in table.foreign_keys:
        # Skip reverse relationships
        if not any(col.name == fk.column_name for col in table.columns):
            continue

        # Skip relationships without relation_type
        if not fk.relation_type:
            continue

        # Get the target table
        target_table = next((t for t in tables.values() if t.name == fk.foreign_table_name), None)
        if not target_table:
            continue

        # Generate the relationship field name (typically plural for collections)
        field_name = fk.foreign_table_name.lower()
        if fk.relation_type in [RelationType.ONE_TO_MANY, RelationType.MANY_TO_MANY]:
            # Make plural for collections
            if not field_name.endswith('s'):
                field_name += 's'

        # Generate the model class name for the related table
        related_class_name = to_pascal_case(fk.foreign_table_name)

        # Generate the field type based on the relationship type
        field_type = get_relationship_field_type(fk.relation_type, related_class_name)

        # Add the relationship field
        relationship_fields.append(f'    {field_name}: {field_type} = None')

    return relationship_fields


def generate_pydantic_model(
    table: TableInfo, tables: dict[str, TableInfo], model_type: WriterClassType = WriterClassType.BASE
) -> str:
    """Generate a Pydantic model for a table."""
    # Generate the model name
    model_name = generate_pydantic_model_name(table.name, model_type)

    # Prepare model content
    model_lines = [f'class {model_name}(BaseModel):']

    # Add docstring
    model_lines.append(f'    """{table.name} model."""')

    # Generate field definitions
    field_lines = []

    # Add fields based on columns
    for column in table.columns:
        # Skip identity columns for insert models
        if model_type == WriterClassType.INSERT and column.is_identity:
            continue

        # Make fields optional for update models
        if model_type == WriterClassType.UPDATE:
            field_type = f'{column.datatype} | None'
            default_value = ' = None'
        else:
            field_type = get_column_type_annotation(column)
            default_value = ' = None' if column.is_nullable else ''

        # Add Field with metadata if needed
        field_metadata = []

        if column.alias:
            field_metadata.append(f"alias='{column.alias}'")

        if column.primary:
            field_metadata.append('primary_key=True')

        if column.unique:
            field_metadata.append('unique=True')

        # Generate the field line
        if field_metadata:
            field_line = f'    {column.name}: {field_type} = Field({", ".join(field_metadata)}){default_value}'
        else:
            field_line = f'    {column.name}: {field_type}{default_value}'

        field_lines.append(field_line)

    # Add relationship fields
    relationship_fields = generate_relationship_fields(table, tables, model_type)
    if relationship_fields:
        field_lines.extend(relationship_fields)

    # Add model configuration if needed
    config_lines = []
    if any(col.alias for col in table.columns):
        config_lines = ['    class Config:', '        populate_by_name = True', '        orm_mode = True']

    # Combine all parts
    model_lines.extend(field_lines)
    if config_lines:
        model_lines.append('')  # Empty line before config
        model_lines.extend(config_lines)

    return '\n'.join(model_lines)


def generate_pydantic_models(tables: list[TableInfo]) -> str:
    """Generate all Pydantic models for the given tables."""
    # Organize tables by name for easier lookup
    tables_dict = {table.name: table for table in tables}

    code_parts = []

    # Generate imports
    imports = get_required_imports(tables)
    code_parts.append('\n'.join(sorted(imports)))
    code_parts.append('')  # Empty line after imports

    # Generate enums
    enums_code = generate_enum_classes(tables)
    if enums_code:
        code_parts.append(enums_code)
        code_parts.append('')  # Empty line after enums

    # Generate models for each table
    for table in tables:
        # Generate base model
        base_model = generate_pydantic_model(table, tables_dict, WriterClassType.BASE)
        code_parts.append(base_model)
        code_parts.append('')  # Empty line after model

        # Generate insert model
        insert_model = generate_pydantic_model(table, tables_dict, WriterClassType.INSERT)
        code_parts.append(insert_model)
        code_parts.append('')  # Empty line after model

        # Generate update model
        update_model = generate_pydantic_model(table, tables_dict, WriterClassType.UPDATE)
        code_parts.append(update_model)
        code_parts.append('')  # Empty line after model

    return '\n'.join(code_parts)


def generate_models(tables: list[TableInfo], orm_type: OrmType, schema: str = 'public') -> str:
    """Generate models based on the ORM type."""
    if orm_type == OrmType.PYDANTIC:
        return generate_pydantic_models(tables)

    # Add SQLAlchemy generation if needed
    logging.warning(f'Model generation for {orm_type} not implemented yet')
    return '# Not implemented'
