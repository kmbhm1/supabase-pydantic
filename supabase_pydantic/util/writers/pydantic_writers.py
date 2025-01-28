import re
from typing import Any

from supabase_pydantic.util.constants import (
    CUSTOM_MODEL_NAME,
    WriterClassType,
)
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, SortedColumns, TableInfo
from supabase_pydantic.util.util import get_pydantic_type
from supabase_pydantic.util.writers.abstract_classes import AbstractClassWriter, AbstractFileWriter
from supabase_pydantic.util.writers.util import get_base_class_post_script as post
from supabase_pydantic.util.writers.util import get_section_comment

# FastAPI


class PydanticFastAPIClassWriter(AbstractClassWriter):
    def __init__(
        self, table: TableInfo, class_type: WriterClassType = WriterClassType.BASE, null_defaults: bool = False
    ):
        super().__init__(table, class_type, null_defaults)

        self.separated_columns: SortedColumns = self.table.sort_and_separate_columns(
            separate_nullable=False, separate_primary_key=True
        )

    def write_name(self) -> str:
        """Method to generate the header for the base class."""
        return f'{self.name}' + f'{post(self.table.table_type, self.class_type)}'

    def write_metaclass(self, metaclasses: list[str] | None = None) -> str | None:
        """Method to generate the metaclasses for the class."""
        metaclasses = metaclasses or []
        if len(metaclasses) > 0:
            return ', '.join(metaclasses)
        if self.class_type == WriterClassType.PARENT or self.class_type == WriterClassType.BASE:
            return CUSTOM_MODEL_NAME
        else:
            metaclasses.append(f'{self.name}{post(self.table.table_type, WriterClassType.PARENT)}')
        return ', '.join(metaclasses)

    def _parse_length_constraint(self, constraint_def: str | None) -> dict[str, int] | None:
        """Parse length constraints from a CHECK constraint definition.

        Args:
            constraint_def: SQL constraint definition string

        Returns:
            Dictionary with min_length and/or max_length if constraints found, None otherwise
        """
        if not constraint_def:
            return None

        length_pattern = r'length\((\w+)\)\s*([=<>]+)\s*(\d+)'
        matches = re.findall(length_pattern, constraint_def)

        if not matches:
            return None

        result = {}
        for _, operator, value in matches:
            value = int(value)
            if operator == '=':
                result['min_length'] = value
                result['max_length'] = value
            elif operator == '>=':
                result['min_length'] = value
            elif operator == '<=':
                result['max_length'] = value

        return result if result else None

    def write_column(self, c: ColumnInfo) -> str:
        """Write a column definition for a Pydantic model."""
        base_type = get_pydantic_type(c.post_gres_datatype, ('str', None))[0]

        # Handle length constraints for text fields
        length_constraints = None
        if c.post_gres_datatype.lower() == 'text' and c.constraint_definition:
            length_constraints = self._parse_length_constraint(c.constraint_definition)

        # Build the type annotation
        if length_constraints and base_type == 'str':
            constraints = {}
            if 'min_length' in length_constraints:
                constraints['min_length'] = length_constraints['min_length']
            if 'max_length' in length_constraints:
                constraints['max_length'] = length_constraints['max_length']

            type_str = f'Annotated[str, StringConstraints(**{constraints})]'
        else:
            type_str = base_type

        # Add nullable type if needed
        type_str = f'{type_str} | None' if (c.is_nullable or self._null_defaults) else type_str

        # Build field values
        field_values = {}
        if (c.is_nullable is not None and c.is_nullable) or self._null_defaults:
            field_values['default'] = 'None'
        if c.alias is not None:
            field_values['alias'] = f'"{c.alias}"'

        # Construct the final column definition
        col = f'{c.name}: {type_str}'
        if field_values:
            col += ' = Field(' + ', '.join([f'{k}={v}' for k, v in field_values.items()]) + ')'

        return col

    def write_docs(self) -> str:
        """Method to generate the docstrings for the class."""
        qualifier = '(Nullable) Parent' if self._null_defaults else 'Base'
        return f'\n\t"""{self.name} {qualifier} Schema."""\n\n'

    def write_primary_keys(self) -> str | None:
        """Method to generate primary key definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.primary_keys]
        return AbstractClassWriter.column_section('Primary Keys', cols) if len(cols) > 0 else None

    def write_primary_columns(self) -> str | None:
        """Method to generate column definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.remaining]
        if len(cols) == 0:
            return None
        return AbstractClassWriter.column_section('Columns', cols)

    def write_foreign_columns(self, use_base: bool = True) -> str | None:
        """Method to generate foreign column definitions for the class."""
        if len(self.table.foreign_keys) == 0:
            return None

        _n = AbstractClassWriter._proper_name

        def _col(x: ForeignKeyInfo) -> str:  # nullable foreign key
            return f'{x.foreign_table_name.lower()}: list[{_n(x.foreign_table_name)}] | None = Field(default=None)'

        fks = [_col(fk) for fk in self.table.foreign_keys]

        return AbstractClassWriter.column_section('Foreign Keys', fks) if len(fks) > 0 else None

    def write_operational_class(self) -> str | None:
        """Method to generate operational class definitions."""
        m = self.write_name()
        op_class = [
            f'class {self.name}({m}):',
            f'\t"""{self.name} Schema for Pydantic.',
            f'\n\tInherits from {m}. Add any customization here.',
            '\t"""',
        ]
        if len(self.table.foreign_keys) > 0:
            fcols = self.write_foreign_columns(use_base=False)
            if fcols is not None:
                op_class.append('\n' + fcols)
        else:  # add a pass statement if there are no foreign keys
            op_class.append('\tpass')

        return '\n'.join(op_class)


class PydanticFastAPIWriter(AbstractFileWriter):
    def __init__(
        self,
        tables: list[TableInfo],
        file_path: str,
        writer: type[AbstractClassWriter] = PydanticFastAPIClassWriter,
        add_null_parent_classes: bool = False,
    ):
        super().__init__(tables, file_path, writer, add_null_parent_classes)

    def _dt_imports(self, imports: set, default_import: tuple[Any, Any | None] = (Any, None)) -> None:
        """Update the imports with the necessary data types."""

        def _pyi(c: ColumnInfo) -> str | None:  # pyi = pydantic import  # noqa
            return get_pydantic_type(c.post_gres_datatype, default_import)[1]

        # column data types
        imports.update(filter(None, map(_pyi, (c for t in self.tables for c in t.columns))))

    def write_imports(self) -> str:
        """Method to generate the imports for the file."""
        # standard
        imports = {
            'from pydantic import BaseModel',
            'from pydantic import Field',
            'from pydantic import Annotated',
            'from pydantic.types import StringConstraints',
        }
        if any([len(t.table_dependencies()) > 0 for t in self.tables]):
            imports.add('from __future__ import annotations')

        # column data types
        self._dt_imports(imports)

        return '\n'.join(sorted(imports))

    def _class_writer_helper(
        self,
        comment_title: str,
        comments: list[str] = [],
        classes_override: list[str] = [],
        is_base: bool = True,
        class_type: WriterClassType = WriterClassType.BASE,
        **kwargs: Any,
    ) -> str:
        sxn = get_section_comment(comment_title, comments)
        classes = classes_override

        if len(classes_override) == 0:
            attr = 'write_class' if is_base else 'write_operational_class'

            def _method(t: TableInfo) -> Any:
                if class_type == WriterClassType.PARENT:
                    return getattr(self.writer(t, class_type, True), attr)
                elif class_type == WriterClassType.BASE_WITH_PARENT:
                    return getattr(self.writer(t, class_type, False), attr)
                return getattr(self.writer(t), attr)

            if len(kwargs) > 0:
                classes = [_method(t)(**kwargs) for t in self.tables]
            else:
                classes = [_method(t)() for t in self.tables]

        return self.join([sxn, *classes])

    def write_custom_classes(self) -> str | None:
        """Method to generate the custom classes for the file."""
        b = 'BaseModel'
        return self._class_writer_helper(
            comment_title='Custom Classes',
            comments=['This is a custom model class for defining common features among Pydantic Base Schema.'],
            classes_override=[f'class {CUSTOM_MODEL_NAME}({b}):\n\tpass'],
        )

    def write_base_classes(self) -> str:
        """Method to generate the base & parent classes for the file."""
        if self.add_null_parent_classes:
            return (
                self._class_writer_helper(
                    'Parent Classes',
                    comments=[
                        'This is a parent class with all fields as nullable. This is useful for refining your models with inheritance. See https://stackoverflow.com/a/65907609.'  # noqa: E501
                    ],
                    class_type=WriterClassType.PARENT,
                )
                + '\n'
            ) + self._class_writer_helper('Base Classes', class_type=WriterClassType.BASE_WITH_PARENT)

        return self._class_writer_helper('Base Classes')

    def write_operational_classes(self) -> str | None:
        """Method to generate the operational classes for the file."""
        return self._class_writer_helper('Operational Classes', is_base=False)
