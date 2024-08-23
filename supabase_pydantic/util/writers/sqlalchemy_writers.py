from typing import Any

from supabase_pydantic.util.constants import WriterClassType
from supabase_pydantic.util.dataclasses import ColumnInfo, SortedColumns, TableInfo
from supabase_pydantic.util.util import get_sqlalchemy_v2_type, to_pascal_case
from supabase_pydantic.util.writers.abstract_classes import AbstractClassWriter, AbstractFileWriter
from supabase_pydantic.util.writers.util import get_section_comment

# FastAPI


class SqlAlchemyFastAPIClassWriter(AbstractClassWriter):
    def __init__(
        self, table: TableInfo, class_type: WriterClassType = WriterClassType.BASE, null_defaults: bool = False
    ):
        super().__init__(table, class_type, null_defaults)
        self._tname = to_pascal_case(self.table.name)
        self.separated_columns: SortedColumns = self.table.sort_and_separate_columns(
            separate_nullable=True, separate_primary_key=True
        )

    def write_name(self) -> str:
        """Method to generate the header for the base class."""
        return self._tname

    def write_metaclass(self, metaclasses: list[str] | None = None) -> str | None:
        """Method to generate the metaclasses for the class."""
        return 'Base'

    def write_docs(self) -> str:
        """Method to generate the docstrings for the class."""
        qualifier = 'Nullable Base' if self._null_defaults else 'Base'
        return f'\n\t"""{self._tname} {qualifier}."""\n\n\t__tablename__ = "{self.table.name}"\n\n'

    def write_column(self, c: ColumnInfo) -> str:
        """Method to generate column definition for the class."""
        # base type
        base_type, pyth_type, _ = get_sqlalchemy_v2_type(c.post_gres_datatype)
        if base_type.lower() == 'uuid':
            base_type = 'UUID(as_uuid=True)'
        if 'time zone' in c.post_gres_datatype.lower():
            base_type = 'TIMESTAMP(timezone=True)'
        col_dtype = f'{pyth_type}' + (' | None' if c.is_nullable else '')

        # field values
        field_values = dict()
        field_values_list_first = list()
        if c.primary:
            field_values['primary_key'] = 'True'
        if c.is_unique:
            field_values['unique'] = 'True'
        for fk in self.table.foreign_keys:
            if c.name == fk.column_name:
                field_values_list_first.append(f'ForeignKey("{fk.foreign_table_name}.{fk.foreign_column_name}")')

        field_values_string = ', '.join(field_values_list_first) if len(field_values_list_first) > 0 else ''
        if len(field_values) > 0:
            if len(field_values_list_first) > 0:
                field_values_string += ', '
            field_values_string += ', '.join([f'{k}={v}' for k, v in field_values.items()])

        return f'{c.name}: Mapped[{col_dtype}] = mapped_column({base_type}{", " + field_values_string if (field_values_string is not None and bool(field_values_string)) else ""})'  # noqa: E501

    def write_primary_keys(self) -> str | None:
        """Method to generate primary key definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.primary_keys]
        return AbstractClassWriter.column_section('Primary Keys', cols) if len(cols) > 0 else None

    def write_primary_columns(self) -> str | None:
        """Method to generate column definitions for the class."""
        cols = [self.write_column(c) for c in self.separated_columns.non_nullable + self.separated_columns.nullable]
        if len(cols) == 0:
            return None
        return AbstractClassWriter.column_section('Columns', cols)

    def write_foreign_columns(self, use_base: bool = True) -> str | None:
        """Method to generate foreign column definitions for the class."""
        # table args
        table_args = []
        for con in self.table.constraints:
            if con.constraint_type() == 'PRIMARY KEY':
                primary_cols = ', '.join([f"'{c}'" for c in con.columns])
                name_str = f"name='{con.constraint_name}'"
                table_args.append(f'PrimaryKeyConstraint({primary_cols}, {name_str}),')
        table_args.append("{ 'schema': 'public' }")

        class_string = '\t# Table Args\n\t__table_args__ = (\n'
        return class_string + '\n'.join([f'\t\t{a}' for a in table_args]) + '\n\t)\n'

    def write_operational_class(self) -> str | None:
        """Method to generate operational class definitions."""
        return None

    def write_columns(self, add_fk: bool = False) -> str:
        """Method to generate column definitions for the class."""
        keys = self.write_primary_keys()
        cols = self.write_primary_columns()
        fcols = self.write_foreign_columns()

        columns = [x for x in [keys, cols, fcols] if x is not None]
        return '\n\n'.join(columns)


class SqlAlchemyFastAPIWriter(AbstractFileWriter):
    def __init__(
        self,
        tables: list[TableInfo],
        file_path: str,
        writer: type[AbstractClassWriter] = SqlAlchemyFastAPIClassWriter,
        add_null_parent_classes: bool = False,
    ):
        super().__init__(tables, file_path, writer, add_null_parent_classes)

    def _dt_imports(
        self, imports: set, default_import: tuple[Any, Any | None] = ('String,str', 'from sqlalchemy import String')
    ) -> None:
        """Update the imports with the necessary data types."""

        def _pyi(c: ColumnInfo) -> str | None:  # pyi = pydantic import  # noqa
            return get_sqlalchemy_v2_type(c.post_gres_datatype, default_import)[2]

        # column data types
        imports.update(filter(None, map(_pyi, (c for t in self.tables for c in t.columns))))

    def write_imports(self) -> str:
        """Method to generate the imports for the file."""
        # standard
        imports = {
            'from sqlalchemy import ForeignKey',
            'from sqlalchemy.orm import DeclarativeBase',
            'from sqlalchemy.orm import Mapped',
            'from sqlalchemy.orm import mapped_column',
        }
        if any([len(t.primary_key()) > 0 for t in self.tables]):
            imports.add('from sqlalchemy import PrimaryKeyConstraint')

        # column data types
        self._dt_imports(imports)

        new_imports = set()
        for i in imports:
            new_imports.update(i.split('\n'))

        return '\n'.join(sorted(new_imports))

    def _class_writer_helper(
        self,
        comment_title: str,
        comments: list[str] = [],
        classes_override: list[str] = [],
        is_base: bool = True,
        **kwargs: Any,
    ) -> str:
        sxn = get_section_comment(comment_title, comments)
        classes = classes_override
        if len(classes_override) == 0:
            attr = 'write_class' if is_base else 'write_operational_class'

            def _method(t: TableInfo) -> Any:
                return getattr(self.writer(t), attr)

            if 'add_fk' in kwargs:
                classes = [_method(t)(add_fk=kwargs['add_fk']) for t in self.tables]
            else:
                classes = [_method(t)() for t in self.tables]

        return self.join([sxn, *classes])

    def write_custom_classes(self, add_fk: bool = False) -> str:
        """Method to write the complete class definition."""
        declarative_base_class = (
            'class Base(DeclarativeBase):\n\t'
            '"""Declarative Base Class."""\n\t'
            '# type_annotation_map = {}\n\n\t'
            'pass'
        )
        return self._class_writer_helper(
            comment_title='Declarative Base',
            classes_override=[declarative_base_class],
        )

    def write_base_classes(self) -> str:
        """Method to write the base classes."""
        return self._class_writer_helper('Base Classes')

    def write_operational_classes(self) -> str | None:
        """Method to write the operational classes."""
        return None
