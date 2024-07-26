from abc import ABC, abstractmethod
from pathlib import Path

from supabase_pydantic.util.constants import BASE_CLASS_POSTFIX
from supabase_pydantic.util.dataclasses import TableInfo
from supabase_pydantic.util.util import to_pascal_case
from supabase_pydantic.util.writers.util import generate_unique_filename


class AbstractClassWriter(ABC):
    def __init__(self, table: TableInfo, nullify_base_schema_class: bool = False):
        self.table = table
        self.nullify_base_schema_class = nullify_base_schema_class
        self.name = to_pascal_case(self.table.name)

    @staticmethod
    def _proper_name(name: str, use_base: bool = False) -> str:
        return to_pascal_case(name) + (BASE_CLASS_POSTFIX if use_base else '')

    def write_class(self, add_fk: bool = False) -> str:
        """Method to write the complete class definition."""
        return self.write_definition() + self.write_docs() + self.write_columns(add_fk)

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
        metas = self.write_metaclass()
        return f'class {self.write_name()}' + (f'({metas}):' if metas is not None else ':')

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
    def __init__(self, tables: list[TableInfo], file_path: str, writer: type[AbstractClassWriter]):
        self.tables = tables
        self.file_path = file_path
        self.writer = writer
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

    def save(self, overwrite: bool = False) -> str:
        """Method to save the file."""
        fp = Path(self.file_path)
        base, ext, directory = fp.stem, fp.suffix, str(fp.parent)
        p = generate_unique_filename(base, ext, directory) if not overwrite and fp.exists() else self.file_path
        with open(p, 'w') as f:
            f.write(self.write())

        return p

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
