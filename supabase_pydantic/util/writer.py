from supabase_pydantic.util.constants import (
    BASE_CLASS_POSTFIX,
    CUSTOM_JSONAPI_META_MODEL_NAME,
    CUSTOM_MODEL_NAME,
    PYDANTIC_TYPE_MAP,
    SQLALCHEMY_TYPE_MAP,
    RelationType,
)
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, FrameworkType, OrmType, TableInfo
from supabase_pydantic.util.string import to_pascal_case


class ClassWriter:
    def __init__(
        self,
        table: TableInfo,
        file_type: OrmType | str = OrmType.PYDANTIC,
        framework_type: FrameworkType | str = FrameworkType.FASTAPI,
        nullify_base_schema_class: bool = False,
    ):
        self.table = table
        self.file_type = OrmType.from_string(file_type) if isinstance(file_type, str) else file_type
        self.framework_type = (
            FrameworkType.from_string(framework_type) if isinstance(framework_type, str) else framework_type
        )
        self.nullify_base_schema_class = nullify_base_schema_class

    # Write class string
    def write(self) -> str:
        """Write the class string."""
        return self.write_base_class_header_string() + self.write_columns()

    def write_working_class(self) -> str | None:
        """Generate the working class string for a table."""

        if self.file_type == OrmType.PYDANTIC:
            if self.framework_type == FrameworkType.FASTAPI:
                to_join = [
                    f'class {to_pascal_case(self.table.name)}({self.write_base_class_name()}):',
                    f'\t"""{to_pascal_case(self.table.name)} Schema for Pydantic.',
                    f'\n\tInherits from {self.write_base_class_name()}. Add any customization here.',
                    '\t"""',
                ]

                # add foreign keys
                foreign_columns = [
                    self.write_foreign_table_column(fk, False, False, True)  # need to feed is_base, here, etc.
                    for fk in self.table.foreign_keys
                ]
                if len(foreign_columns) > 0:
                    to_join.append('\n\t# Foreign Keys\n' + '\n'.join([f'\t{c}' for c in foreign_columns]))
                else:
                    to_join.append('\tpass')

                return '\n'.join(to_join)

            else:  # FrameworkType.FASTAPI_JSONAPI
                jsonapi_class_types = ['Patch', 'Input', 'Item']
                working_classes = [
                    '\n'.join(
                        [
                            f'class {to_pascal_case(self.table.name)}{t}Schema({self.write_base_class_name()}):',
                            f'\t"""{to_pascal_case(self.table.name)} {t.upper()} Schema."""',
                            '\tpass',
                        ]
                    )
                    for t in jsonapi_class_types
                ]

                # return working_class_string
                return '\n\n'.join(working_classes)
        return None

    # Base class headers
    def write_base_class_name(self) -> str:
        """Generate the class name of the base class."""
        if self.file_type == OrmType.SQLALCHEMY:
            return to_pascal_case(self.table.name)

        post = 'View' + BASE_CLASS_POSTFIX if self.table.table_type == 'VIEW' else BASE_CLASS_POSTFIX
        nullable_post = 'Nullable' if self.nullify_base_schema_class else ''
        return f'{to_pascal_case(self.table.name)}{post}{nullable_post}'

    def write_base_class_docstring(self) -> str:
        """Generate the docstring for the base class.

        Newlines and tabs are added for better readability.
        """
        if self.file_type == OrmType.SQLALCHEMY:
            return f'\n\t"""{to_pascal_case(self.table.name)} Base."""\n\n\t__tablename__ = "{self.table.name}"\n\n'
        base_description = 'Nullable Base' if self.nullify_base_schema_class else 'Base'
        return f'\n\t"""{to_pascal_case(self.table.name)} {base_description} Schema."""\n\n'

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

        # Developer's Note: self.nullify_base_schema_class only affects Pydantic models for now

        if self.file_type == OrmType.SQLALCHEMY:
            base_type = SQLALCHEMY_TYPE_MAP.get(c.post_gres_datatype, ('String', None))[0]
            if base_type.lower() == 'uuid':
                base_type = 'UUID(as_uuid=True)'
            if 'time zone' in c.post_gres_datatype.lower():
                base_type = 'TIMESTAMP(timezone=True)'

            return base_type

        else:
            base_type = PYDANTIC_TYPE_MAP.get(c.post_gres_datatype, ('str', None))[0]
            return f'{base_type} | None' if (c.is_nullable or self.nullify_base_schema_class) else base_type

    def write_column_field_values(self, c: ColumnInfo) -> str | None:
        """Generate the field values for a column."""
        field_values = dict()
        field_values_list_first = list()

        # Developer's Note: self.nullify_base_schema_class only affects Pydantic models for now

        if self.file_type == OrmType.SQLALCHEMY:
            if c.is_nullable:
                field_values['nullable'] = 'True'
            if c.primary:
                field_values['primary_key'] = 'True'
            if c.is_unique:
                field_values['unique'] = 'True'
            for fk in self.table.foreign_keys:
                if c.name == fk.column_name:
                    field_values_list_first.append(f'ForeignKey("{fk.foreign_table_name}.{fk.foreign_column_name}")')

        else:  # OrmType.PYDANTIC
            if (c.is_nullable is not None and c.is_nullable) or self.nullify_base_schema_class:
                field_values['default'] = 'None'
            if c.alias is not None:
                field_values['alias'] = f'"{c.alias}"'

        field_values_string = ', '.join(field_values_list_first) if len(field_values_list_first) > 0 else ''
        if len(field_values) > 0:
            if len(field_values_list_first) > 0:
                field_values_string += ', '
            field_values_string += ', '.join([f'{k}={v}' for k, v in field_values.items()])

        return field_values_string

    def write_column(self, c: ColumnInfo) -> str:
        """Generate the column string for a table."""
        base_type = self.write_column_base_type(c)
        field_values = self.write_column_field_values(c)

        if self.file_type == OrmType.SQLALCHEMY:
            return f'{c.name} = Column({base_type}{", " + field_values if (field_values is not None and bool(field_values)) else ""})'  # noqa: E501
        else:
            column_string = f'{c.name}: {base_type}'
            if field_values is not None and bool(field_values):
                column_string += f' = Field({field_values})'
            return column_string

    # TODO
    # 1. need a solution for is_base and is_view feeding into this fn
    # 2. need ability to add None as default value
    # 3. need ability check one to many, etc. relationships and adjust this line accordingly
    def write_foreign_table_column(
        self, fk: ForeignKeyInfo, is_base: bool = False, is_view: bool = False, is_nullable: bool = True
    ) -> str:
        """Generate the column string for a foreign table."""
        post = ('View' if is_view else '') + (BASE_CLASS_POSTFIX if is_base else '')
        foreign_table_name = f'{to_pascal_case(fk.foreign_table_name)}{post}'
        column_name = fk.foreign_table_name.lower()

        # SQLALCHEMY
        if self.file_type == OrmType.SQLALCHEMY:
            if self.framework_type == FrameworkType.FASTAPI_JSONAPI:
                if self.table.name == 'case_reviews' or self.table.name == 'cases':
                    print(self.table.name, fk.relation_type, fk.foreign_table_name, fk.foreign_column_name)
                back_populates = f'back_populates="{to_pascal_case(self.table.name)}"'
                useList = ', useList=True' if fk.relation_type != RelationType.ONE_TO_ONE else ''
                relationship = f'relationship("{to_pascal_case(fk.foreign_table_name)}", {back_populates}{useList})'
                base_type = f'Mapped[{to_pascal_case(fk.foreign_table_name)}]'

                return f'{column_name}: {base_type} = {relationship}'

        # PYDANTIC
        base_type = f'list[{foreign_table_name}]'
        if is_nullable:
            base_type += ' | None'

        # Add annotated for base schema mypy translations
        # if not is_base:
        #     base_schema_name = f'{to_pascal_case(fk.foreign_table_name)}{BASE_CLASS_POSTFIX}'
        #     base_type = f'Annotated[{base_type}, {base_schema_name}.{column_name}]'

        if self.file_type == OrmType.PYDANTIC:
            if self.framework_type == FrameworkType.FASTAPI:
                return f'{column_name}: {base_type}' + (' = Field(default=None)' if is_nullable else '')
            else:  # FrameworkType.FASTAPI_JSONAPI
                is_list = fk.relation_type != RelationType.ONE_TO_ONE
                base_type = base_type if is_list else foreign_table_name
                if is_nullable and not is_list:
                    base_type += ' | None'
                resource_type = column_name

                return (
                    f'{column_name}: {base_type} = Field('
                    + '\n\t\trelationsip=RelationshipInfo('
                    + f'\n\t\t\tresource_type="{resource_type}"'
                    + (',\n\t\t\tmany=True' if is_list else '')
                    + '\n\t\t),'
                    + '\n\t)'
                )

        return None

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

        # TODO: implement table sorting method here
        if self.file_type == OrmType.SQLALCHEMY:
            nullable_columns = [self.write_column(c) for c in sorted_columns if c.is_nullable]
            non_nullable_columns = [self.write_column(c) for c in sorted_columns if not c.is_nullable]
            columns = non_nullable_columns + nullable_columns
        else:
            columns = [self.write_column(c) for c in sorted_columns]

        foreign_columns = [
            x
            for x in (
                [
                    self.write_foreign_table_column(fk, True, False, True)  # need to feed is_base, here, etc.
                    for fk in self.table.foreign_keys
                ]
            )
            if x is not None
        ]
        table_args = self.write_table_args()

        class_string = ''
        if len(primary_columns) > 0:
            class_string += '\t# Primary Keys\n' + '\n'.join([f'\t{c}' for c in primary_columns])
        if len(columns) > 0:
            if len(primary_columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Columns\n' + '\n'.join([f'\t{c}' for c in columns])
        if len(foreign_columns) > 0:
            if len(primary_columns) > 0 or len(columns) > 0:
                class_string += '\n\n'
            comment = 'Foreign Keys' if self.framework_type == FrameworkType.FASTAPI else 'Relationships'
            class_string += f'\t# {comment}\n' + '\n'.join([f'\t{c}' for c in foreign_columns])
        if len(table_args) > 0 and self.file_type == OrmType.SQLALCHEMY:
            if len(primary_columns) > 0 or len(columns) > 0:
                class_string += '\n\n'
            class_string += '\t# Table Args\n\t__table_args__ = (\n'
            class_string += '\n'.join([f'\t\t{arg}' for arg in table_args]) + '\n\t)\n'

        return class_string


class FileWriter:
    def __init__(
        self,
        tables: list[TableInfo],
        file_type: OrmType | str = OrmType.PYDANTIC,
        framework_type: FrameworkType | str = FrameworkType.FASTAPI,
        nullify_base_schema_class: bool = False,
    ):
        self.tables = tables
        self.file_type = OrmType.from_string(file_type) if isinstance(file_type, str) else file_type
        self.framework_type = (
            FrameworkType.from_string(framework_type) if isinstance(framework_type, str) else framework_type
        )
        self.nullify_base_schema_class = nullify_base_schema_class

    def write(self, path: str, overwrite: bool = True):
        """Write the models file to a provided path."""

        # imports
        imports_string = self.write_imports()

        # custom
        custom_model_section, custom_model_string = '', ''
        if self.file_type == OrmType.PYDANTIC:
            custom_model_section = self.write_custom_model_section_comment()
            custom_model_string = self.write_custom_model_string()
        if self.file_type == OrmType.SQLALCHEMY:
            custom_model_section = self.write_declarative_base_section_comment()
            custom_model_string = self.write_declarative_base_string()

        # base classes
        base_section = self.write_base_section_comment()
        base_string = '\n\n\n'.join([self.write_table_class(t) for t in self.tables])

        # working classes
        working_string = self.write_working_classes()
        working_section = ''
        if bool(working_string):
            working_section = self.write_working_section_comment()

        # final file string
        final_sections = [imports_string, base_section, base_string]
        if bool(custom_model_string):
            final_sections.insert(1, custom_model_section)
            final_sections.insert(2, custom_model_string)
        if bool(working_string):
            final_sections.append(working_section)
            final_sections.append(working_string)
        file_string = '\n\n\n'.join(final_sections) + '\n\n\n'

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
                    imports.add('from sqlalchemy.orm import relationship')
                    imports.add('from sqlalchemy.orm import Mapped')
                    imports.add('from __future__ import annotations')

                # both
                imports.add('from sqlalchemy.ext.declarative import declarative_base')
                imports.add('from sqlalchemy import Column')
                imports.add('from sqlalchemy import ForeignKey')
                if len(table.primary_key()) > 0:
                    imports.add('from sqlalchemy import PrimaryKeyConstraint')

            elif self.file_type == OrmType.PYDANTIC:
                if self.framework_type == FrameworkType.FASTAPI_JSONAPI:
                    imports.add('from pydantic import BaseModel as PydanticBaseModel')
                    imports.add('from fastapi_jsonapi.schema_base import RelationshipInfo')
                    imports.add('from fastapi_jsonapi.schema_base import Field')
                else:
                    imports.add('from pydantic import BaseModel')
                    imports.add('from pydantic import Field')

                # if len(table.foreign_keys) > 0:
                #     imports.add('from typing import Annotated')

                # both
                if len(table.table_dependencies()) > 0:
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
        class_writer = ClassWriter(table, self.file_type, self.framework_type, self.nullify_base_schema_class)
        return class_writer.write()

    def write_working_class(self, table: TableInfo) -> str:
        """Generate the working class string for a table."""
        class_writer = ClassWriter(table, self.file_type, self.framework_type, self.nullify_base_schema_class)
        return class_writer.write_working_class()

    def write_working_classes(self) -> str:
        """Generate the working class strings for all tables.

        This function contains the logic to handle when and how working classes
        should be written.
        """
        if self.file_type == OrmType.PYDANTIC:
            if self.framework_type == FrameworkType.FASTAPI:
                return '\n\n\n'.join([self.write_working_class(t) for t in self.tables])
            else:  # FrameworkType.FASTAPI_JSONAPI
                return '\n\n\n'.join([f'# {t.name}\n' + self.write_working_class(t) for t in self.tables])
        return ''

    def write_all_classes(self, table: TableInfo) -> tuple[str, str]:
        """Generate the working class string for a table.

        Helper method to generate both the working class and the base class.

        Returns:
            tuple[str, str]: The base class string and the working class string
        """
        class_writer = ClassWriter(table, self.file_type, self.framework_type, self.nullify_base_schema_class)
        return class_writer.write(), class_writer.write_working_class()

    def write_custom_model_string(self) -> str:
        """Generate a custom Pydantic model."""
        b = 'BaseModel' if self.framework_type == FrameworkType.FASTAPI else CUSTOM_JSONAPI_META_MODEL_NAME
        return f'class {CUSTOM_MODEL_NAME}({b}):\n\tpass'

    def write_declarative_base_string(self) -> str:
        """Generate the declarative base string for SQLAlchemy."""
        return 'Base = declarative_base()'

    # Comments
    def write_base_section_comment(self) -> str:
        """Generate the base section comment."""
        return '#' * 30 + ' Base Classes'

    def write_custom_model_section_comment(self) -> str:
        """Generate the custom model section comment."""
        return (
            '#' * 30
            + ' Custom Models'
            + '\n# Note: This is a custom model class for defining common features among Pydantic Base Schema.'
        )

    def write_working_section_comment(self) -> str:
        """Generate the working section comment."""
        return '#' * 30 + ' Working Classes'

    def write_declarative_base_section_comment(self) -> str:
        """Generate the declarative base section comment."""
        return '#' * 30 + ' Declarative Base'
