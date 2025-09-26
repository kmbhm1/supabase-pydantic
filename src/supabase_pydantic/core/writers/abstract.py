from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path

from inflection import singularize

from supabase_pydantic.core.constants import BASE_CLASS_POSTFIX, WriterClassType
from supabase_pydantic.core.writers.utils import generate_unique_filename
from supabase_pydantic.db.database_type import DatabaseType
from supabase_pydantic.db.models import TableInfo
from supabase_pydantic.utils.strings import to_pascal_case


def get_section_comment(title: str, description_lines: list[str] | None = None) -> str:
    """Generate a section comment with a title and optional description lines.

    Args:
        title: Title of the section
        description_lines: Optional list of description lines to add after title

    Returns:
        Formatted section comment string
    """
    if description_lines is None:
        description_lines = []

    lines = [f'# {title}', '#']
    for line in description_lines:
        lines.append(f'# {line}')

    return '\n'.join(lines)


class AbstractClassWriter(ABC):
    def __init__(
        self,
        table: TableInfo,
        class_type: WriterClassType = WriterClassType.BASE,
        null_defaults: bool = False,
        singular_names: bool = False,
        database_type: DatabaseType = DatabaseType.POSTGRES,
    ):
        self.table = table
        self.class_type = class_type
        self._null_defaults = null_defaults
        self.singular_names = singular_names
        self.name = self._generate_class_name(self.table.name)
        self.database_type = database_type

    def _generate_class_name(self, table_name: str) -> str:
        """Generate class name from table name, optionally singularizing it."""
        name = singularize(table_name) if self.singular_names else table_name
        return to_pascal_case(name)  # type: ignore

    def _proper_name(self, name: str, use_base: bool = False) -> str:
        """Generate proper class name, optionally singularizing it."""
        processed_name = singularize(name) if self.singular_names else name
        result: str = to_pascal_case(processed_name) + (BASE_CLASS_POSTFIX if use_base else '')
        return result

    def write_class(
        self,
        add_fk: bool = False,
    ) -> str:
        """Method to write the complete class definition."""
        class_def: str = self.write_definition() + self.write_docs() + self.write_columns(add_fk)
        return class_def

    @abstractmethod
    def write_operational_class(self) -> str | None:
        """Method to generate operational class definitions."""
        return None

    @abstractmethod
    def write_name(self) -> str:
        """Method to generate the header for the base class."""
        raise NotImplementedError('write_name not implemented')

    @abstractmethod
    def write_metaclass(self, metaclasses: list[str] | None = None) -> str | None:
        """Method to generate the metaclasses for the class."""
        raise NotImplementedError('write_metaclass not implemented')

    @abstractmethod
    def write_docs(self) -> str:
        """Method to generate the docstrings for the class."""
        raise NotImplementedError('write_docs not implemented')

    def write_definition(self) -> str:
        """Method to generate the class definition for the class."""
        name = self.write_name()
        metaclass = self.write_metaclass()
        result = f'class {name}({metaclass}):' if metaclass else f'class {name}:'

        # print(f'\nwrite_definition() for table {self.table.name}:')
        # print(f'  class_type: {self.class_type}')
        # print(f'  name: {name}')
        # print(f'  metaclass: {metaclass}')
        # print(f'  result: {result}')
        return result

    @abstractmethod
    def write_primary_keys(self) -> str | None:
        """Method to generate primary key definitions for the class."""
        raise NotImplementedError('write_primary_keys not implemented')

    @abstractmethod
    def write_primary_columns(self) -> str | None:
        """Method to generate column definitions for the class."""
        raise NotImplementedError('write_primary_columns not implemented')

    @abstractmethod
    def write_foreign_columns(self, use_base: bool = False) -> str | None:
        """Method to generate foreign column definitions for the class."""
        raise NotImplementedError('write_foreign_columns not implemented')

    @staticmethod
    def column_section(comment_title: str, columns: list[str]) -> str:
        """Method to generate a section of columns."""
        return f'\t# {comment_title}\n' + '\n'.join([f'\t{c}' for c in columns])

    def write_columns(self, add_fk: bool = False) -> str:
        """Method to generate column definitions for the class."""
        keys = self.write_primary_keys()
        cols = self.write_primary_columns()
        fcols = self.write_foreign_columns() if add_fk else None

        columns = [x for x in [keys, cols, fcols] if x is not None]
        return '\n\n'.join(columns)


class AbstractFileWriter(ABC):
    def __init__(
        self,
        tables: list[TableInfo],
        file_path: str,
        writer: Callable[..., AbstractClassWriter],
        add_null_parent_classes: bool = False,
        singular_names: bool = False,
        database_type: DatabaseType = DatabaseType.POSTGRES,
    ):
        self.tables = tables
        self.file_path = file_path
        self.add_null_parent_classes = add_null_parent_classes
        self.singular_names = singular_names
        self.writer = writer
        self.database_type = database_type
        self.jstr = '\n\n\n'

    def write(self) -> str:
        """Method to write the complete file."""
        # order is important here
        parts = [
            self.write_imports(),
            self.write_custom_classes(),
            self.write_base_classes(),
            self.write_operational_classes(),
        ]

        # filter None and join parts
        return self.jstr.join(p for p in parts if p is not None) + '\n'

    def save(self, overwrite: bool = False) -> tuple[str, str | None]:
        """Method to save the file."""
        fp = Path(self.file_path)
        base, ext, directory = fp.stem, fp.suffix, str(fp.parent)
        latest_file = os.path.join(directory, f'{base}_latest{ext}')
        with open(latest_file, 'w') as f:
            f.write(self.write())

        if not overwrite:
            versioned_file = generate_unique_filename(base, ext, directory)
            with open(versioned_file, 'w') as f:
                f.write(self.write())

            return latest_file, versioned_file

        return latest_file, None

    def join(self, strings: list[str]) -> str:
        """Method to join strings."""
        return self.jstr.join(strings)

    @abstractmethod
    def write_imports(self) -> str:
        """Method to generate import statements for the file."""
        raise NotImplementedError('write_imports not implemented')

    @abstractmethod
    def write_custom_classes(self) -> str | None:
        """Method to generate custom class definitions for the file."""
        raise NotImplementedError('write_custom_classes not implemented')

    @abstractmethod
    def write_base_classes(self) -> str:
        """Method to generate class definitions for the file."""
        raise NotImplementedError('write_base_classes not implemented')

    @abstractmethod
    def write_operational_classes(self) -> str | None:
        """Method to generate operational class definitions for the file."""
        raise NotImplementedError('write_operational_classes not implemented')
