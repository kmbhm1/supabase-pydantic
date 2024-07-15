from enum import Enum
from typing import Any
from supabase_pydantic.util.constants import (
    BASE_CLASS_POSTFIX,
    CUSTOM_MODEL_NAME,
    PYDANTIC_TYPE_MAP,
    SQLALCHEMY_TYPE_MAP,
)
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, TableInfo
from supabase_pydantic.util.generator_helpers import write_custom_model_string
from supabase_pydantic.util.string import to_pascal_case


def add_from_string(cls: Any) -> Any:
    @classmethod
    def from_string(cls, value: str):
        value_lower = value.lower()
        for member in cls:
            if member.value == value_lower:
                return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

    cls.from_string = from_string
    return cls


@add_from_string
class OrmType(Enum):
    """Enum for file types."""

    PYDANTIC = 'pydantic'
    SQLALCHEMY = 'sqlalchemy'


@add_from_string
class FrameworkType(Enum):
    """Enum for framework types."""

    FASTAPI = 'fastapi'
    FASTAPI_JSONAPI = 'fastapi-jsonapi'


class ClassWriter:
    def __init__(
        self,
        table: TableInfo,
        file_type: OrmType | str = OrmType.PYDANTIC,
        framework_type: FrameworkType | str = FrameworkType.FASTAPI,
    ):
        self.table = table
        self.file_type = OrmType.from_string(file_type) if isinstance(file_type, str) else file_type
        self.framework_type = (
            FrameworkType.from_string(framework_type) if isinstance(framework_type, str) else framework_type
        )

        self.base_class_name = self.write_base_class_name()

    # Write entire class string
    def write(self) -> str:
        """Write the class string."""
        return self.write_base_class_header_string() + self.write_columns()

    # Base class headers
    def write_base_class_name(self) -> str:
        """Generate the class name of the base class."""
        if self.file_type == OrmType.SQLALCHEMY:
            return to_pascal_case(self.table.name)

        post = 'View' + BASE_CLASS_POSTFIX if self.table.table_type == 'VIEW' else BASE_CLASS_POSTFIX
        return f'{to_pascal_case(self.table.name)}{post}'

    def write_base_class_docstring(self) -> str:
        """Generate the docstring for the base class.

        Newlines and tabs are added for better readability.
        """
        if self.file_type == OrmType.SQLALCHEMY:
            return f'\n\t"""{to_pascal_case(self.table.name)} Base."""\n\n\t__tablename__ = "{self.table.name}"\n'
        return f'\n\t"""{to_pascal_case(self.table.name)} Base Schema."""\n'

    def write_base_class_meta_string(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str | None:
        """Generate the meta string for the base class."""
        if self.file_type == OrmType.SQLALCHEMY:
            return 'Base'

        if isinstance(metaclass, list) and len(metaclass) == 0:
            return None
        return ', '.join(metaclass) if isinstance(metaclass, list) else metaclass

    def write_base_class_header_string(self, metaclass: str | list[str] = CUSTOM_MODEL_NAME) -> str:
        """Generate the base class header string for a table."""
        metas = self.write_base_class_meta_string(metaclass)

        return (
            f'class {self.write_base_class_name()}'
            + (f'({metas}):' if metas is not None else ':')
            + self.write_base_class_docstring()
        )

    # Class Columns
    def write_column_base_type(self, c: ColumnInfo) -> str:
        """Generate the base type for a column."""
        if self.file_type == OrmType.SQLALCHEMY:
            base_type = SQLALCHEMY_TYPE_MAP.get(c.post_gres_datatype, ('String', None))[0]
            if base_type.lower() == 'uuid':
                base_type = 'UUID(as_uuid=True)'
            if 'time zone' in c.post_gres_datatype.lower():
                base_type = 'TIMESTAMP(timezone=True)'

            return base_type

        else:
            base_type = PYDANTIC_TYPE_MAP.get(c.post_gres_datatype, ('str', None))[0]
            return f'{base_type} | None' if c.is_nullable else base_type

    def write_column_field_values(self, c: ColumnInfo) -> str | None:
        """Generate the field values for a column."""
        field_values = dict()

        if self.file_type == OrmType.SQLALCHEMY:
            field_values['nullable'] = 'True' if c.is_nullable else 'False'
            if c.primary:
                field_values['primary_key'] = 'True'

        else:
            if c.is_nullable is not None and c.is_nullable:
                field_values['default'] = 'None'
            if c.alias is not None:
                field_values['alias'] = f'"{c.alias}"'

        return ', '.join([f'{k}={v}' for k, v in field_values.items()]) if len(field_values) > 0 else None

    def write_column(self, c: ColumnInfo) -> str:
        """Generate the column string for a table."""
        base_type = self.write_column_base_type(c)
        field_values = self.write_column_field_values(c)

        if self.file_type == OrmType.SQLALCHEMY:
            return f'{c.name} = Column({base_type}{", " + field_values if field_values is not None else ""})'
        else:
            column_string = f'{c.name}: {base_type}'
            if field_values is not None:
                column_string += f' = Field({field_values})'
            return column_string

    # TODO
    # 1. need a solution for is_base and is_view feeding into this fn
    # 2. need ability to add None as default value
    # 3. need ability check one to many, etc. relationships and adjust this line accordingly
    def write_foreign_table_column(self, fk: ForeignKeyInfo, is_base: bool = False, is_view: bool = False) -> str:
        """Generate the column string for a foreign table."""
        post = ('View' if is_view else '') + (BASE_CLASS_POSTFIX if is_base else '')
        foreign_table_name = f'{to_pascal_case(fk.foreign_table_name)}{post}'
        base_type = f'list[{foreign_table_name}]'
        if is_base:
            base_type += ' | None'

        return f'{fk.foreign_table_name.lower()}: {base_type} = None'

    def write_table_args(self) -> list[str]:
        """Generate the table args for a table."""
        table_args = []
        for con in self.table.constraints:
            if con.constraint_type() == 'PRIMARY KEY':
                primary_cols = ', '.join([f"'{c}'" for c in con.columns])
                name_str = f"name='{con.constraint_name}'"
                table_args.append(f'PrimaryKeyConstraint({primary_cols}, {name_str}),')
        table_args.append("{ 'schema': 'public' }")

        return table_args

    # TODO:
    # 1. need to add adaptation for writing Base Schemas, nullified base schemas, view schemas, and working classes
    def write_columns(self) -> str:
        """Generate the column strings for a table."""
        primary_columns = [self.write_column(c) for c in self.table.get_primary_columns()]
        sorted_columns = sorted(self.table.get_secondary_columns(), key=lambda x: x.name)
        columns = [self.write_column(c) for c in sorted_columns]
        foreign_columns = [
            self.write_foreign_table_column(fk, True, False)  # need to feed is_base, here, etc.
            for fk in self.table.foreign_keys
        ]
        table_args = self.write_table_args()

        class_string = ''
        if len(primary_columns) > 0:
            class_string += '\t# Primary Keys\n'
            class_string += '\n'.join([f'\t{c}' for c in primary_columns])
        if len(columns) > 0:
            if len(primary_columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Columns\n'
            class_string += '\n'.join([f'\t{c}' for c in columns])
        if len(foreign_columns) > 0 and self.file_type == OrmType.PYDANTIC:
            if len(primary_columns) > 0 or len(columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Foreign Keys\n' + '\n'.join([f'\t{c}' for c in foreign_columns])
        if len(table_args) > 0 and self.file_type == OrmType.SQLALCHEMY:
            class_string += '\n\n'
            class_string += '\t# Table Args\n'
            class_string += '\t__table_args__ = (\n'
            class_string += '\n'.join([f'\t\t{arg}' for arg in table_args])
            class_string += '\n\t)\n'

        return class_string


class FileWriter:
    def __init__(
        self,
        tables: list[TableInfo],
        file_type: OrmType | str = OrmType.PYDANTIC,
        framework_type: FrameworkType | str = FrameworkType.FASTAPI,
    ):
        self.tables = tables
        self.file_type = OrmType.from_string(file_type) if isinstance(file_type, str) else file_type
        self.framework_type = (
            FrameworkType.from_string(framework_type) if isinstance(framework_type, str) else framework_type
        )

    def write(self, path: str, overwrite: bool = True):
        """Write the file to the given path."""
        # imports
        imports_string = self.write_imports()

        # custom models
        custom_model_section, custom_model_string = '', ''
        if self.file_type == OrmType.PYDANTIC:
            custom_model_section = self.write_custom_model_section_comment()
            custom_model_string = write_custom_model_string()

        # base classes
        base_section = self.write_base_section_comment()
        base_string = '\n\n\n'.join([self.write_table_class(t) for t in self.tables])

        # TODO: add working classes
        # working_section = self.write_working_section_comment()
        # working_string = ''  # TODO: implement writer

        # final file string
        file_string = (
            '\n\n\n'.join(
                [
                    imports_string,
                    custom_model_section,
                    custom_model_string,
                    base_section,
                    base_string,
                    # working_section,
                    # working_string,
                ]
            )
            + '\n\n\n'
        )

        # write to file
        with open(path, 'w' if overwrite else 'a') as f:
            f.write(file_string)

    # Imports
    def _write_standard_imports(self) -> set[str]:
        """Generate the standard imports for the file."""
        imports = set()

        for table in self.tables:
            if self.file_type == OrmType.SQLALCHEMY:
                if self.framework_type == FrameworkType.FASTAPI_JSONAPI:
                    imports.add('from sqlalchemy.ext.declarative import declarative_base')
                    imports.add('from sqlalchemy import ForeignKey')
                    imports.add('from sqlalchemy.orm import relationship')

                # both
                imports.add('from sqlalchemy.ext.declarative import declarative_base')
                imports.add('from sqlalchemy import Column')
                if len(table.primary_key()) > 0:
                    imports.add('from sqlalchemy import PrimaryKeyConstraint')

            elif self.file_type == OrmType.PYDANTIC:
                if self.framework_type == FrameworkType.FASTAPI_JSONAPI:
                    imports.add('from pydantic import BaseModel as PydanticBaseModel')
                    imports.add('from fastapi_jsonapi.schema_base import BaseModel, Field, RelationshipInfo')
                else:
                    imports.add('from pydantic import BaseModel')
                    imports.add('from pydantic import Field')

                # both
                if len(table.table_dependencies()) > 0:
                    # imports.add('from typing import ForwardRef')
                    imports.add('from __future__ import annotations')

        return imports

    def _write_data_type_imports(self) -> set[str]:
        """Generate the data type imports for the file."""
        imports = set()
        fb = 'from sqlalchemy import Column' if self.file_type == OrmType.SQLALCHEMY else None
        type_map = PYDANTIC_TYPE_MAP if self.file_type == OrmType.PYDANTIC else SQLALCHEMY_TYPE_MAP

        for table in self.tables:
            for column in table.columns:
                t = column.post_gres_datatype
                res = type_map.get(t, ('Any', fb))[1]
                if res is not None:
                    imports.add(res)

        return imports

    def write_imports(self) -> str:
        """Generate the import statements for the file with newlines."""
        imports = set()

        imports.update(self._write_standard_imports())
        imports.update(self._write_data_type_imports())

        return '\n'.join(sorted(imports))

    # Classes
    def write_table_class(self, table: TableInfo) -> str:
        """Generate the class string for a table."""
        class_writer = ClassWriter(table, self.file_type, self.framework_type)
        return class_writer.write()

    # Comments
    def write_base_section_comment(self) -> str:
        """Generate the base section comment."""
        return '#' * 30 + ' Base Classes'

    def write_custom_model_section_comment(self) -> str:
        """Generate the custom model section comment."""
        return (
            '#' * 30
            + ' Custom Models'
            + '\n# Note: This is a custom model class for defining common features amongst Base Schema.'
        )

    def write_working_section_comment(self) -> str:
        """Generate the working section comment."""
        return '#' * 30 + ' Working Classes'
