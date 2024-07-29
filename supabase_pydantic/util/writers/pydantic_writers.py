from typing import Any

from supabase_pydantic.util.constants import (
    CUSTOM_JSONAPI_META_MODEL_NAME,
    CUSTOM_MODEL_NAME,
    RelationType,
)
from supabase_pydantic.util.dataclasses import ColumnInfo, ForeignKeyInfo, SortedColumns, TableInfo
from supabase_pydantic.util.util import get_pydantic_type
from supabase_pydantic.util.writers.abstract_classes import AbstractClassWriter, AbstractFileWriter
from supabase_pydantic.util.writers.util import get_base_class_post_script as post
from supabase_pydantic.util.writers.util import get_section_comment

# FastAPI


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
        if metaclasses is not None and (isinstance(metaclasses, list), len(metaclasses) > 0):
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

    def write_docs(self) -> str:
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
        self, tables: list[TableInfo], file_path: str, writer: type[AbstractClassWriter] = PydanticFastAPIClassWriter
    ):
        super().__init__(tables, file_path, writer)

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


# FastAPI-JSONAPI


class PydanticJSONAPIClassWriter(PydanticFastAPIClassWriter):
    def __init__(self, table: TableInfo, nullify_base_schema_class: bool = False):
        super().__init__(table, nullify_base_schema_class)

    def write_foreign_columns(self, use_base: bool = True) -> str | None:
        """Method to generate foreign column definitions for the class."""
        if len(self.table.foreign_keys) == 0:
            return None

        _n = AbstractClassWriter._proper_name

        def _names(name: str) -> tuple[str, str]:
            return _n(name, use_base), name.lower()

        def _base(name: str, is_list: bool) -> str:
            return f'{f"list[{name}]" if is_list else name} | None'

        fks = []
        for fk in self.table.foreign_keys:
            is_list = fk.relation_type != RelationType.ONE_TO_ONE
            forn, coln = _names(fk.foreign_table_name)

            fks.append(
                f'{coln}: {_base(forn, is_list)} = Field('
                + '\n\t\trelationsip=RelationshipInfo('
                + f'\n\t\t\tresource_type="{coln}"'
                + (',\n\t\t\tmany=True' if is_list else '')
                + '\n\t\t),'
                + '\n\t)'
            )

        return AbstractClassWriter.column_section('Relationships', fks) if len(fks) > 0 else None

    def write_operational_class(self) -> str | None:
        """Method to generate operational class definitions."""
        class_types = ['Patch', 'Input', 'Item']
        classes = [
            '\n'.join(
                [
                    f'class {self.name}{t}Schema({self.write_name()}):',
                    f'\t"""{self.name} {t.upper()} Schema."""',
                    '\tpass',
                ]
            )
            for t in class_types
        ]

        return '\n\n'.join(classes)

    def write_columns(self, add_fk: bool = False) -> str:
        """Method to generate column definitions for the class."""
        keys = self.write_primary_keys()
        cols = self.write_primary_columns()
        fcols = self.write_foreign_columns()

        columns = [x for x in [keys, cols, fcols] if x is not None]
        return '\n\n'.join(columns)


class PydanticJSONAPIWriter(PydanticFastAPIWriter):
    def __init__(self, tables: list[TableInfo], file_path: str):
        super().__init__(tables, file_path, PydanticJSONAPIClassWriter)

    def write_imports(self) -> str:
        """Method to generate the imports for the file."""
        # standard
        imports = {
            'from fastapi_jsonapi.schema_base import Field, RelationshipInfo',
            'from pydantic import BaseModel as PydanticBaseModel',
        }
        if any([len(t.table_dependencies()) > 0 for t in self.tables]):
            imports.add('from __future__ import annotations')

        # column data types
        self._dt_imports(imports)

        return '\n'.join(sorted(imports))

    def write_custom_classes(self) -> str | None:
        """Method to generate the custom classes for the file."""
        b = CUSTOM_JSONAPI_META_MODEL_NAME
        return self._class_writer_helper(
            comment_title='Custom Classes',
            comments=['This is a custom model class for defining common features among Pydantic Base Schema.'],
            classes_override=[f'class {CUSTOM_MODEL_NAME}({b}):\n\tpass'],
        )
