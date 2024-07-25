from supabase_pydantic.util.constants import BASE_CLASS_POSTFIX, CUSTOM_MODEL_NAME
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, SortedColumns, TableInfo
from supabase_pydantic.util.string import to_pascal_case
from supabase_pydantic.util.util import get_pydantic_type
from supabase_pydantic.util.writers.abstract_classes import AbstractClassWriter, AbstractFileWriter
from supabase_pydantic.util.writers.util import get_base_class_post_script as post
from supabase_pydantic.util.writers.util import get_section_comment


class PydanticFastAPIClassWriter(AbstractClassWriter):
    def __init__(self, table: TableInfo, nullify_base_schema_class: bool = False):
        super().__init__(table, nullify_base_schema_class)

        self.separated_columns: SortedColumns = self.table.sort_and_separate_columns(
            separate_nullable=False, separate_primary_key=True
        )

    def write_name(self) -> str:
        """Method to generate the header for the base class."""
        return f'{self.name}' + f'{post(self.table.table_type, self.nullify_base_schema_class)}'

    def write_metaclass(self, metaclasses: list[str] | None = None) -> str | None:
        """Method to generate the metaclasses for the class."""
        if metaclasses is not None:
            return ', '.join(metaclasses)
        return CUSTOM_MODEL_NAME

    def write_column(self, c: ColumnInfo) -> str:
        """Method to generate the column definition for the class."""
        base_type = get_pydantic_type(c.post_gres_datatype, ('str', None))[0]
        base_type = f'{base_type} | None' if (c.is_nullable or self.nullify_base_schema_class) else base_type

        field_values = dict()
        if (c.is_nullable is not None and c.is_nullable) or self.nullify_base_schema_class:
            field_values['default'] = 'None'
        if c.alias is not None:
            field_values['alias'] = f'"{c.alias}"'

        col = f'{c.name}: {base_type}'
        if len(field_values) > 0:
            col += ' = Field(' + ', '.join([f'{k}={v}' for k, v in field_values.items()]) + ')'

        return col

    def write_docs(self):
        """Method to generate the docstrings for the class."""
        qualifier = 'Nullable Base' if self.nullify_base_schema_class else 'Base'
        return f'\n\t"""{self.name} {qualifier} Schema."""\n\n'

    def write_primary_keys(self) -> str | None:
        """Method to generate primary key definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.primary_keys]
        return AbstractClassWriter.column_section('Primary Keys', cols) if len(cols) > 0 else None

    def write_primary_columns(self) -> str | None:
        """Method to generate column definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.remaining]
        return AbstractClassWriter.column_section('Columns', cols)

    def write_foreign_columns(self, use_base: bool = True) -> str | None:
        """Method to generate foreign column definitions for the class."""
        if len(self.table.foreign_keys) == 0:
            return None

        def n(name: str):
            return to_pascal_case(name) + (BASE_CLASS_POSTFIX if use_base else '')

        def col(x: ForeignKeyInfo):  # nullable foreign key
            return f'{x.foreign_table_name.lower()}: list[{n(x.foreign_table_name)}] | None = Field(default=None)'

        fks = [col(fk) for fk in self.table.foreign_keys]

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
            op_class.append(self.write_foreign_columns(use_base=False))
        else:  # add a pass statement if there are no foreign keys
            op_class.append('\tpass')

        return '\n'.join(op_class)


class PydanticFastAPIWriter(AbstractFileWriter):
    def __init__(self, tables: list[TableInfo], file_path: str):
        super().__init__(tables, file_path, PydanticFastAPIClassWriter)

    def write_imports(self) -> str:
        """Method to generate the imports for the file."""
        default_import = ('Any', None)

        def pyi(c: ColumnInfo):  # pyi = pydantic import  # noqa
            return get_pydantic_type(c.post_gres_datatype, default_import)[1]

        # standard
        imports = {
            'from pydantic import BaseModel',
            'from pydantic import Field',
        }
        if any([len(t.table_dependencies()) > 0 for t in self.tables]):
            imports.add('from __future__ import annotations')

        # column data types
        imports.update(filter(None, map(pyi, (c for t in self.tables for c in t.columns))))

        return '\n'.join(sorted(imports))

    def _class_writer_helper(
        self, comment_title: str, comments: list[str] = [], classes_override: list[str] = [], is_base: bool = True
    ) -> str | None:
        sxn = get_section_comment(comment_title, comments)
        classes = classes_override
        if len(classes_override) == 0:
            attr = 'write_class' if is_base else 'write_operational_class'

            def method(t: TableInfo):
                return getattr(self.writer(t), attr)

            classes = [method(t)() for t in self.tables]

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
        """Method to generate the base classes for the file."""
        return self._class_writer_helper('Base Classes')

    def write_operational_classes(self) -> str | None:
        """Method to generate the operational classes for the file."""
        return self._class_writer_helper('Operational Classes', is_base=False)
